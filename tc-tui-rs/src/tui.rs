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
    widgets::{Block, Borders, Paragraph},
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
        InputMode::Normal => Style::default(),
        InputMode::Editing => Style::default().fg(Color::Yellow),
    };

    let input = Paragraph::new(app.input.as_str())
        .style(input_style)
        .block(Block::default().borders(Borders::ALL).title("Search Indicators"));
    f.render_widget(input, header_chunks[0]);

    // Format stats
    let avg_rating = app.stats.avg_rating.map_or("N/A".to_string(), |r| format!("{:.1}", r));
    let avg_conf = app.stats.avg_confidence.map_or("N/A".to_string(), |c| format!("{:.1}%", c));

    let stats_text = vec![
        Line::from(vec![
            Span::styled("Count: ", Style::default().add_modifier(Modifier::BOLD)),
            Span::raw(format!("{}   ", app.stats.total_count)),
            Span::styled("Owners: ", Style::default().add_modifier(Modifier::BOLD)),
            Span::raw(format!("{}   ", app.stats.unique_owners)),
            Span::styled("Avg Rating: ", Style::default().add_modifier(Modifier::BOLD)),
            Span::raw(format!("{}   ", avg_rating)),
            Span::styled("Avg Conf: ", Style::default().add_modifier(Modifier::BOLD)),
            Span::raw(format!("{}", avg_conf)),
        ]),
        Line::from(vec![
             Span::styled("Active: ", Style::default().add_modifier(Modifier::BOLD)),
             Span::raw(format!("{}   ", app.stats.active_count)),
             Span::styled("False Positives: ", Style::default().add_modifier(Modifier::BOLD)),
             Span::raw(format!("{}   ", app.stats.false_positives)),
        ])
    ];

    let stats_paragraph = Paragraph::new(stats_text)
        .block(Block::default().borders(Borders::TOP).title("Search Stats"))
        .style(Style::default().fg(Color::Cyan));

    f.render_widget(stats_paragraph, header_chunks[1]);


    // --- Carousel (Main Content) ---

    let carousel_area = chunks[1];
    let block = Block::default().borders(Borders::ALL).title("Indicator Results");

    if app.grouped_results.is_empty() {
        let text = Paragraph::new("No results found. Press 'e' to search.")
            .alignment(Alignment::Center)
            .block(block);
        f.render_widget(text, carousel_area);
    } else {
        let group = &app.grouped_results[app.selected_index];
        let current_index = app.selected_index + 1;
        let total = app.grouped_results.len();

        let card_title = format!(" Item {} of {} | Use ←/→ to navigate | ↑/↓ to scroll ", current_index, total);
        let card_block = Block::default()
            .borders(Borders::ALL)
            .title(card_title)
            .border_style(Style::default().fg(Color::White));

        // Content of the card
        let mut content = vec![];

        // Header info for the group
        content.push(Line::from(vec![
            Span::styled("Summary: ", Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)),
            Span::styled(group.summary.clone(), Style::default().add_modifier(Modifier::BOLD).fg(Color::White)),
        ]));
        content.push(Line::from(vec![
            Span::styled("Type: ", Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)),
            Span::raw(group.indicator_type.clone()),
        ]));
        content.push(Line::from(""));
        content.push(Line::from(Span::raw("─".repeat(carousel_area.width as usize - 4))));

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

            content.push(Line::from(vec![
                Span::styled("Owner: ", Style::default().fg(Color::Green).add_modifier(Modifier::BOLD)),
                Span::raw(indicator.owner_name.clone()),
            ]));

            content.push(Line::from(vec![
                Span::styled("Rating: ", Style::default().fg(Color::Yellow)),
                Span::raw(format!("{} ({:.1})", rating_skulls, indicator.rating)),
                Span::raw(" | "),
                Span::styled("Confidence: ", Style::default().fg(Color::Yellow)),
                Span::raw(format!("{}%", indicator.confidence)),
                Span::raw(" | "),
                Span::styled("Active: ", Style::default().fg(Color::Yellow)),
                Span::raw(if indicator.active { "Yes" } else { "No" }),
            ]));

            content.push(Line::from(vec![
                Span::styled("Added: ", Style::default().fg(Color::Blue)),
                Span::raw(indicator.date_added.format("%Y-%m-%d %H:%M").to_string()),
                Span::raw(" | "),
                Span::styled("Modified: ", Style::default().fg(Color::Blue)),
                Span::raw(indicator.last_modified.format("%Y-%m-%d %H:%M").to_string()),
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
            .alignment(Alignment::Left) // Left alignment for list of details
            .scroll((app.scroll_offset, 0));

        f.render_widget(paragraph, carousel_area);
    }

    // --- Footer ---
    let footer_text = vec![
        Line::from(vec![
            Span::styled(" ←/→ ", Style::default().fg(Color::Yellow)),
            Span::raw("Next/Prev Group  |  "),
            Span::styled(" ↑/↓ ", Style::default().fg(Color::Yellow)),
            Span::raw("Scroll  |  "),
            Span::styled(" e ", Style::default().fg(Color::Yellow)),
            Span::raw("Search  |  "),
            Span::styled(" q ", Style::default().fg(Color::Yellow)),
            Span::raw("Quit"),
        ]),
        Line::from(app.status_message.clone()),
    ];
    let footer = Paragraph::new(footer_text)
        .block(Block::default().borders(Borders::ALL).title("Status"));
    f.render_widget(footer, chunks[2]);

    // Set cursor
    if let InputMode::Editing = app.input_mode {
        f.set_cursor_position(ratatui::layout::Position::new(
            header_chunks[0].x + app.input.len() as u16 + 1,
            header_chunks[0].y + 1,
        ))
    }
}
