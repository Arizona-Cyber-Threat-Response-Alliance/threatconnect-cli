use crossterm::{
    event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    backend::{Backend, CrosstermBackend},
    layout::{Constraint, Direction, Layout},
    style::{Color, Style},
    text::{Line, Span},
    widgets::{Block, Borders, List, ListItem, Paragraph, ListState},
    Frame, Terminal,
};
use std::{error::Error, io, sync::Arc};
use tokio::sync::Mutex;
use crate::api::ThreatConnectClient;
use crate::models::Indicator;

enum InputMode {
    Normal,
    Editing,
}

pub struct App {
    input: String,
    input_mode: InputMode,
    results: Vec<Indicator>,
    results_state: ListState,
    client: Arc<ThreatConnectClient>,
    status_message: String,
}

impl App {
    pub fn new(client: Arc<ThreatConnectClient>) -> App {
        App {
            input: String::new(),
            input_mode: InputMode::Normal,
            results: Vec::new(),
            results_state: ListState::default(),
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
            ("resultLimit", "100"),
            ("sorting", "dateAdded ASC")
        ];

        match self.client.get::<crate::models::search::SearchResponse>("/indicators", Some(&params)).await {
            Ok(response) => {
                self.results = response.data;
                self.status_message = format!("Found {} results.", self.results.len());
                self.results_state.select(Some(0));
            }
            Err(e) => {
                self.status_message = format!("Search failed: {}", e);
                self.results.clear();
                self.results_state.select(None);
            }
        }
    }

    fn next(&mut self) {
        let i = match self.results_state.selected() {
            Some(i) => {
                if i >= self.results.len() - 1 {
                    0
                } else {
                    i + 1
                }
            }
            None => 0,
        };
        self.results_state.select(Some(i));
    }

    fn previous(&mut self) {
        let i = match self.results_state.selected() {
            Some(i) => {
                if i == 0 {
                    self.results.len() - 1
                } else {
                    i - 1
                }
            }
            None => 0,
        };
        self.results_state.select(Some(i));
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

        // Small timeout to prevent blocking everything, though usually event::read blocks
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
                        KeyCode::Down => {
                            app_guard.next();
                        }
                        KeyCode::Up => {
                            app_guard.previous();
                        }
                        _ => {}
                    },
                    InputMode::Editing => match key.code {
                        KeyCode::Enter => {
                            // Trigger search
                            drop(app_guard); // Release lock before async call

                            // We need to clone the app or handle this better for async call in loop
                            // For simplicity in this structure, we'll re-acquire lock inside perform_search logic
                            // or just do it here if possible.
                            // Ideally, we'd channel events. But let's try to keep it simple.
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
        .margin(2)
        .constraints(
            [
                Constraint::Length(3),
                Constraint::Min(1),
                Constraint::Length(3),
            ]
            .as_ref(),
        )
        .split(f.area());

    let input_style = match app.input_mode {
        InputMode::Normal => Style::default(),
        InputMode::Editing => Style::default().fg(Color::Yellow),
    };

    let input = Paragraph::new(app.input.as_str())
        .style(input_style)
        .block(Block::default().borders(Borders::ALL).title("Search Indicators"));
    f.render_widget(input, chunks[0]);

    let items: Vec<ListItem> = app
        .results
        .iter()
        .map(|i| {
            let rating_skulls = "💀".repeat(i.rating.round() as usize);
            let rating_str = format!("{} ({}/5.0)", rating_skulls, i.rating);

            let content = vec![
                Line::from(vec![
                    Span::styled("Summary: ", Style::default().fg(Color::Red).add_modifier(ratatui::style::Modifier::BOLD)),
                    Span::raw(i.summary.clone()),
                ]),
                Line::from(vec![
                    Span::styled("Date Added: ", Style::default().fg(Color::Red).add_modifier(ratatui::style::Modifier::BOLD)),
                    Span::raw(i.date_added.format("%B %d, %Y %H:%M:%S").to_string()),
                ]),
                Line::from(vec![
                    Span::styled("Last Modified: ", Style::default().fg(Color::Red).add_modifier(ratatui::style::Modifier::BOLD)),
                    Span::raw(i.last_modified.format("%B %d, %Y %H:%M:%S").to_string()),
                ]),
                Line::from(vec![
                    Span::styled("Type: ", Style::default().fg(Color::Red).add_modifier(ratatui::style::Modifier::BOLD)),
                    Span::raw(i.type_.clone()),
                ]),
                Line::from(vec![
                    Span::styled("Rating: ", Style::default().fg(Color::Red).add_modifier(ratatui::style::Modifier::BOLD)),
                    Span::raw(rating_str),
                ]),
                Line::from(vec![
                    Span::styled("Confidence: ", Style::default().fg(Color::Red).add_modifier(ratatui::style::Modifier::BOLD)),
                    Span::raw(format!("{}%", i.confidence)),
                ]),
                Line::from(vec![
                    Span::styled("Owner: ", Style::default().fg(Color::Red).add_modifier(ratatui::style::Modifier::BOLD)),
                    Span::raw(i.owner_name.clone()),
                ]),
                Line::from(vec![
                    Span::styled("Active: ", Style::default().fg(Color::Red).add_modifier(ratatui::style::Modifier::BOLD)),
                    Span::raw(if i.active { "Yes" } else { "No" }),
                ]),
                Line::from(vec![
                    Span::styled("Web Link: ", Style::default().fg(Color::Red).add_modifier(ratatui::style::Modifier::BOLD)),
                    Span::raw(i.web_link.clone()),
                ]),
                Line::from(vec![
                    Span::styled("Source: ", Style::default().fg(Color::Red).add_modifier(ratatui::style::Modifier::BOLD)),
                    Span::raw(i.source.clone().unwrap_or_else(|| "N/A".to_string())),
                ]),
                Line::from(""),
                Line::from(Span::styled("Description:", Style::default().fg(Color::Red).add_modifier(ratatui::style::Modifier::BOLD))),
                Line::from(i.description.clone().unwrap_or_else(|| "No description available.".to_string())),
                Line::from(""),
                Line::from(Span::raw("-".repeat(40))),
                Line::from(""),
            ];
            ListItem::new(content)
        })
        .collect();

    let results_list = List::new(items)
        .block(Block::default().borders(Borders::ALL).title("Results"))
        .highlight_style(Style::default().add_modifier(ratatui::style::Modifier::REVERSED));

    f.render_stateful_widget(results_list, chunks[1], &mut app.results_state);

    let status = Paragraph::new(app.status_message.as_str())
        .block(Block::default().borders(Borders::ALL).title("Status"));
    f.render_widget(status, chunks[2]);

    // Set cursor if editing
    if let InputMode::Editing = app.input_mode {
        f.set_cursor_position(ratatui::layout::Position::new(
            chunks[0].x + app.input.len() as u16 + 1,
            chunks[0].y + 1,
        ))
    }
}
