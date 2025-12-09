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

                self.status_message = format!("Found {} indicators in {} groups.", self.stats.total_count, self.grouped_results.len());
            }
            Err(e) => {
                self.status_message = format!("Search failed: {}", e);
                self.grouped_results.clear();
                self.stats = SearchStats::default();
                self.selected_index = 0;
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

        let card_title = format!(" Item {} of {} ", current_index, total);
        let card_block = Block::default()
            .borders(Borders::ALL)
            .title(card_title)
            .border_style(Style::default().fg(Color::White));

        // Content of the card
        // We show: Summary, Type, Count in group, etc.
        // For Phase 2, we just render summary and basic info.

        let mut content = vec![
            Line::from(""),
            Line::from(vec![
                Span::styled("Summary: ", Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)),
                Span::styled(group.summary.clone(), Style::default().add_modifier(Modifier::BOLD).fg(Color::White)),
            ]),
            Line::from(vec![
                Span::styled("Type: ", Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)),
                Span::raw(group.indicator_type.clone()),
            ]),
            Line::from(vec![
                Span::styled("Group Size: ", Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)),
                Span::raw(format!("{} record(s)", group.indicators.len())),
            ]),
            Line::from(""),
            Line::from(Span::raw("─".repeat(carousel_area.width as usize - 4))),
            Line::from(""),
        ];

        // Add some details from the first indicator?
        if let Some(first) = group.indicators.first() {
             let rating_skulls = "💀".repeat(first.rating.round() as usize);
             content.push(Line::from(vec![
                Span::styled("Rating: ", Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)),
                Span::raw(format!("{} ({:.1})", rating_skulls, first.rating)),
            ]));
             content.push(Line::from(vec![
                Span::styled("Confidence: ", Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)),
                Span::raw(format!("{}%", first.confidence)),
            ]));
            content.push(Line::from(vec![
                Span::styled("Owner: ", Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)),
                Span::raw(first.owner_name.clone()),
            ]));
             if group.indicators.len() > 1 {
                 content.push(Line::from(Span::styled("(and other owners)", Style::default().fg(Color::DarkGray))));
             }
        }

        let paragraph = Paragraph::new(content)
            .block(card_block)
            .alignment(Alignment::Center); // Or Left? Center might look cool for carousel.

        // Visual Cues for Left/Right
        // We can render arrows on the sides if we split the carousel area horizontally.
        // [ < ] [ Card ] [ > ]
        let layout = Layout::default()
            .direction(Direction::Horizontal)
            .constraints([
                Constraint::Length(3),
                Constraint::Min(10),
                Constraint::Length(3),
            ])
            .split(carousel_area);

        let left_arrow = Paragraph::new("\n\n\n◄").alignment(Alignment::Center).style(Style::default().fg(Color::Yellow));
        let right_arrow = Paragraph::new("\n\n\n►").alignment(Alignment::Center).style(Style::default().fg(Color::Yellow));

        f.render_widget(left_arrow, layout[0]);
        f.render_widget(paragraph, layout[1]);
        f.render_widget(right_arrow, layout[2]);
    }

    // --- Footer ---
    let footer_text = vec![
        Line::from(vec![
            Span::styled(" ←/→ ", Style::default().fg(Color::Yellow)),
            Span::raw("Next/Prev Group  |  "),
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
