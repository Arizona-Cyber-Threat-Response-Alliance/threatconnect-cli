use crossterm::{
    event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    backend::{Backend, CrosstermBackend},
    layout::{Constraint, Direction, Layout, Alignment},
    style::{Color, Style, Modifier},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph, Padding, BorderType},
    Frame, Terminal,
};
use std::{error::Error, io, sync::Arc};
use tokio::sync::Mutex;
use crate::api::ThreatConnectClient;
use crate::logic::aggregation::{GroupedIndicator, SearchStats, group_indicators, calculate_stats};

enum InputMode {
    Normal,
    Editing,
}

pub struct App {
    input: String,
    input_mode: InputMode,
    grouped_results: Vec<GroupedIndicator>,
    selected_index: usize,
    scroll_offset: u16,
    stats: SearchStats,
    client: Arc<ThreatConnectClient>,
    status_message: String,
}

impl App {
    pub fn new(client: Arc<ThreatConnectClient>) -> App {
        App {
            input: String::new(),
            input_mode: InputMode::Normal,
            grouped_results: Vec::new(),
            selected_index: 0,
            scroll_offset: 0,
            stats: SearchStats::default(),
            client,
            status_message: String::from("Press 'q' to quit, 'e' to enter search mode."),
        }
    }

    async fn perform_search(&mut self) {
        if self.input.trim().is_empty() {
            return;
        }

        self.status_message = format!("Searching for '{}'...", self.input);

        // Construct TQL query for summary
        let tql = format!("summary contains \"{}\"", self.input);
        let params = [
            ("tql", tql.as_str()),
            ("resultStart", "0"),
            ("resultLimit", "100"), // We might need pagination later, but 100 is ok for MVP
            ("sorting", "dateAdded ASC")
        ];

        match self.client.get::<crate::models::search::SearchResponse>("/indicators", Some(&params)).await {
            Ok(response) => {
                let indicators = response.data;
                self.stats = calculate_stats(&indicators);
                self.grouped_results = group_indicators(indicators);
                self.selected_index = 0;
                self.scroll_offset = 0;

                self.status_message = format!("Found {} indicators in {} groups.", self.stats.total_count, self.grouped_results.len());
            }
            Err(e) => {
                self.status_message = format!("Search failed: {}", e);
                self.grouped_results.clear();
                self.stats = SearchStats::default();
                self.selected_index = 0;
                self.scroll_offset = 0;
            }
        }
    }

    fn next(&mut self) {
        if self.grouped_results.is_empty() {
            return;
        }
        if self.selected_index >= self.grouped_results.len() - 1 {
            self.selected_index = 0; // Wrap around
        } else {
            self.selected_index += 1;
        }
        self.scroll_offset = 0;
    }

    fn previous(&mut self) {
        if self.grouped_results.is_empty() {
            return;
        }
        if self.selected_index == 0 {
            self.selected_index = self.grouped_results.len() - 1; // Wrap around
        } else {
            self.selected_index -= 1;
        }
        self.scroll_offset = 0;
    }

    fn scroll_down(&mut self) {
        if !self.grouped_results.is_empty() {
            self.scroll_offset = self.scroll_offset.saturating_add(1);
        }
    }

    fn scroll_up(&mut self) {
        if !self.grouped_results.is_empty() {
            self.scroll_offset = self.scroll_offset.saturating_sub(1);
        }
    }
}

pub async fn run_app() -> Result<(), Box<dyn Error>> {
    // Setup terminal
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    // Load env vars
    dotenv::dotenv().ok();
    let access_id = std::env::var("TC_ACCESS_ID").unwrap_or_default();
    let secret_key = std::env::var("TC_SECRET_KEY").unwrap_or_default();
    let instance = std::env::var("TC_INSTANCE").unwrap_or_default();

    let client = Arc::new(ThreatConnectClient::new(access_id, secret_key, instance));
    let app = Arc::new(Mutex::new(App::new(client)));

    let res = run_loop(&mut terminal, app).await;

    // Restore terminal
    disable_raw_mode()?;
    execute!(
        terminal.backend_mut(),
        LeaveAlternateScreen,
        DisableMouseCapture
    )?;
    terminal.show_cursor()?;

    if let Err(err) = res {
        println!("{:?}", err);
    }

    Ok(())
}

async fn run_loop<B: Backend>(terminal: &mut Terminal<B>, app: Arc<Mutex<App>>) -> io::Result<()> {
    loop {
        let mut app_guard = app.lock().await;
        terminal.draw(|f| ui(f, &mut app_guard))?;

        if crossterm::event::poll(std::time::Duration::from_millis(100))? {
            if let Event::Key(key) = event::read()? {
                match app_guard.input_mode {
                    InputMode::Normal => match key.code {
                        KeyCode::Char('e') => {
                            app_guard.input_mode = InputMode::Editing;
                            app_guard.status_message = String::from("Editing... Press Enter to search, Esc to cancel.");
                        }
                        KeyCode::Char('q') => {
                            return Ok(());
                        }
                        KeyCode::Right => {
                            app_guard.next();
                        }
                        KeyCode::Left => {
                            app_guard.previous();
                        }
                        KeyCode::Down => {
                            app_guard.scroll_down();
                        }
                        KeyCode::Up => {
                            app_guard.scroll_up();
                        }
                        _ => {}
                    },
                    InputMode::Editing => match key.code {
                        KeyCode::Enter => {
                            drop(app_guard);
                            let mut app_guard_search = app.lock().await;
                            app_guard_search.perform_search().await;
                            app_guard_search.input_mode = InputMode::Normal;
                        }
                        KeyCode::Char(c) => {
                            app_guard.input.push(c);
                        }
                        KeyCode::Backspace => {
                            app_guard.input.pop();
                        }
                        KeyCode::Esc => {
                            app_guard.input_mode = InputMode::Normal;
                            app_guard.status_message = String::from("Search cancelled.");
                        }
                        _ => {}
                    },
                }
            }
        }
    }
}

fn ui(f: &mut Frame, app: &mut App) {
    // Colors
    const TC_ORANGE: Color = Color::Rgb(255, 122, 79);
    const TC_VERY_DARK_ORANGE: Color = Color::Rgb(163, 76, 0);   // #a34c00
    const TC_DARK_ORANGE: Color = Color::Rgb(254, 124, 80);      // #fe7c50 (Using user's "dark orange" name, though sim to TC_ORANGE)
    const TC_LIGHT_ORANGE: Color = Color::Rgb(250, 198, 148);    // #fac694
    const TC_LIGHT_BLUE: Color = Color::Rgb(179, 209, 247);      // #b3d1f7
    const TC_DARK_BLUE: Color = Color::Rgb(51, 93, 127);         // #335d7f
    const TC_WHITE: Color = Color::White;

    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .margin(1)
        .constraints(
            [
                Constraint::Length(7), // Header: Search + Stats
                Constraint::Min(10),   // Carousel
                Constraint::Length(3), // Footer
            ]
            .as_ref(),
        )
        .split(f.area());

    // --- Header ---
    let header_chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Length(3), Constraint::Length(4)])
        .split(chunks[0]);

    let input_style = match app.input_mode {
        InputMode::Normal => Style::default().fg(TC_WHITE),
        InputMode::Editing => Style::default().fg(TC_ORANGE),
    };

    let input = Paragraph::new(format!("> {}", app.input.as_str()))
        .style(input_style)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .border_type(BorderType::Rounded)
                .title("Search Indicators")
                .border_style(Style::default().fg(TC_ORANGE))
                .padding(Padding::horizontal(4)),
        );
    f.render_widget(input, header_chunks[0]);

    // Format stats
    let avg_rating = app.stats.avg_rating.map_or("N/A".to_string(), |r| format!("{:.1}", r));
    let avg_conf = app.stats.avg_confidence.map_or("N/A".to_string(), |c| format!("{:.1}%", c));

    let stats_text = vec![
        Line::from(vec![
            Span::styled("Count: ", Style::default().add_modifier(Modifier::BOLD).fg(TC_ORANGE)),
            Span::raw(format!("{}   ", app.stats.total_count)),
            Span::styled("Owners: ", Style::default().add_modifier(Modifier::BOLD).fg(TC_ORANGE)),
            Span::raw(format!("{}   ", app.stats.unique_owners)),
            Span::styled("Avg Evilness: ", Style::default().add_modifier(Modifier::BOLD).fg(TC_ORANGE)),
            Span::raw(format!("{}   ", avg_rating)),
            Span::styled("Avg Conf: ", Style::default().add_modifier(Modifier::BOLD).fg(TC_ORANGE)),
            Span::raw(format!("{}", avg_conf)),
        ]),
        Line::from(vec![
            Span::styled("Active: ", Style::default().add_modifier(Modifier::BOLD).fg(TC_ORANGE)),
            Span::raw(format!("{}   ", app.stats.active_count)),
            Span::styled("False Positives: ", Style::default().add_modifier(Modifier::BOLD).fg(TC_ORANGE)),
            Span::raw(format!("{}   ", app.stats.false_positives)),
        ]),
    ];

    let stats_paragraph = Paragraph::new(stats_text)
        .block(
            Block::default()
                .borders(Borders::TOP)
                .title("Search Stats")
                .border_style(Style::default().fg(TC_ORANGE))
                .padding(Padding::horizontal(4)),
        )
        .style(Style::default().fg(TC_WHITE));

    f.render_widget(stats_paragraph, header_chunks[1]);

    // --- Carousel (Main Content) ---

    let carousel_area = chunks[1];
    let block = Block::default()
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .title("Indicator Results")
        .border_style(Style::default().fg(TC_ORANGE))
        .padding(Padding::new(4, 4, 1, 0)); // Top padding 1

    if app.grouped_results.is_empty() {
        let text = Paragraph::new("No results found. Press 'e' to search.")
            .alignment(Alignment::Center)
            .block(block);
        f.render_widget(text, carousel_area);
    } else {
        let group = &app.grouped_results[app.selected_index];
        let current_index = app.selected_index + 1;
        let total = app.grouped_results.len();

        let card_title = format!(" Item {} of {} ", current_index, total);
        let card_block = Block::default()
            .borders(Borders::ALL)
            .border_type(BorderType::Rounded)
            .title(card_title)
            .border_style(Style::default().fg(TC_ORANGE))
            .padding(Padding::new(4, 4, 1, 0)); // Top padding 1

        // Content of the card
        let mut content = vec![];

        // Header info for the group
        content.push(Line::from(vec![
            Span::styled("Summary: ", Style::default().fg(TC_DARK_ORANGE).add_modifier(Modifier::BOLD)),
            Span::styled(group.summary.clone(), Style::default().add_modifier(Modifier::BOLD).fg(TC_WHITE)),
        ]));
        content.push(Line::from(vec![
            Span::styled("Type: ", Style::default().fg(TC_LIGHT_ORANGE).add_modifier(Modifier::BOLD)),
            Span::raw(group.indicator_type.clone()),
        ]));
        // Removed empty line before divider
        let divider_len = carousel_area.width.saturating_sub(10) as usize; // width - borders(2) - padding(8)
        content.push(Line::from(Span::raw("─".repeat(divider_len))));

        // List all indicators
        for (idx, indicator) in group.indicators.iter().enumerate() {
            if idx > 0 {
                content.push(Line::from(""));
                content.push(Line::from(Span::styled("- - - - -", Style::default().fg(Color::DarkGray))));
                content.push(Line::from(""));
            } else {
                content.push(Line::from(""));
            }

            let rating_skulls = "💀".repeat(indicator.rating.round() as usize);

            // Layout:
            // Owner: ... | Active: ...
            // Added: ... | Modified: ...
            // Evilness: ...
            // Confidence: ... [---    ]

            // Line 1
            content.push(Line::from(vec![
                Span::styled("Owner: ", Style::default().fg(TC_DARK_BLUE).add_modifier(Modifier::BOLD)),
                Span::raw(indicator.owner_name.clone()),
                Span::raw(" | "),
                Span::styled("Active: ", Style::default().fg(TC_ORANGE).add_modifier(Modifier::BOLD)),
                Span::raw(if indicator.active { "Yes" } else { "No" }),
            ]));

            // Line 2
            content.push(Line::from(vec![
                Span::styled("Added: ", Style::default().fg(TC_LIGHT_BLUE)),
                Span::raw(indicator.date_added.format("%Y-%m-%d %H:%M").to_string()),
                Span::raw(" | "),
                Span::styled("Modified: ", Style::default().fg(TC_LIGHT_BLUE)),
                Span::raw(indicator.last_modified.format("%Y-%m-%d %H:%M").to_string()),
            ]));

            // Line 3: Evilness
            content.push(Line::from(vec![
                Span::styled("Evilness: ", Style::default().fg(TC_VERY_DARK_ORANGE)),
                Span::raw(format!("{} ({:.1})", rating_skulls, indicator.rating)),
            ]));

            // Line 4: Confidence Bar
            let conf_val = indicator.confidence as u32; // 0-100
            let filled_count = (conf_val as f32 / 10.0).round() as usize;
            let filled_count = filled_count.clamp(0, 10);
            let empty_count = 10 - filled_count;

            let filled_bar = "-".repeat(filled_count);
            let empty_bar = "-".repeat(empty_count);

            content.push(Line::from(vec![
                Span::styled("Confidence: ", Style::default().fg(TC_ORANGE)),
                Span::raw(format!("{}% [", conf_val)),
                Span::styled(filled_bar, Style::default().fg(TC_ORANGE)),
                Span::styled(empty_bar, Style::default().fg(TC_WHITE)),
                Span::raw("]"),
            ]));

            if let Some(desc) = &indicator.description {
                if !desc.is_empty() {
                    content.push(Line::from(Span::styled("Description:", Style::default().add_modifier(Modifier::UNDERLINED))));
                    content.push(Line::from(desc.clone()));
                }
            }
        }

        // Render Paragraph with scroll
        let paragraph = Paragraph::new(content)
            .block(card_block)
            .alignment(Alignment::Left)
            .scroll((app.scroll_offset, 0));

        f.render_widget(paragraph, carousel_area);
    }

    // --- Footer ---
    let footer_text = vec![
        Line::from(vec![
            Span::styled(" ←/→ ", Style::default().fg(TC_ORANGE)),
            Span::raw("Next/Prev Group  |  "),
            Span::styled(" ↑/↓ ", Style::default().fg(TC_ORANGE)),
            Span::raw("Scroll  |  "),
            Span::styled(" e ", Style::default().fg(TC_ORANGE)),
            Span::raw("Search  |  "),
            Span::styled(" q ", Style::default().fg(TC_ORANGE)),
            Span::raw("Quit"),
        ]),
        Line::from(app.status_message.clone()),
    ];
    let footer = Paragraph::new(footer_text)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .border_type(BorderType::Rounded)
                .title("Navigation")
                .border_style(Style::default().fg(TC_ORANGE))
                .padding(Padding::horizontal(4)),
        );
    f.render_widget(footer, chunks[2]);

    // Set cursor
    if let InputMode::Editing = app.input_mode {
        // x = rect.x + border(1) + padding(4) + "> " (2) + input_len
        f.set_cursor_position(ratatui::layout::Position::new(
            header_chunks[0].x + 1 + 4 + 2 + app.input.len() as u16,
            header_chunks[0].y + 1,
        ))
    }
}
