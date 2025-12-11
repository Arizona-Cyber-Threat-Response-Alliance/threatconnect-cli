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

#[derive(Clone, Copy)]
pub enum ThemeVariant {
    ThreatConnect,
    ColorPop,
}

#[derive(Clone)]
pub struct AppTheme {
    pub variant: ThemeVariant,
    pub border: Color,
    pub text: Color,
    pub input_edit: Color,
    pub title_main: Color,     // Stats headers, Input border
    pub title_secondary: Color,// Type, Tags, Assoc
    pub summary_highlight: Color, // Summary
    pub owner_label: Color,
    pub date_label: Color,
    pub active_label: Color,
    pub evilness_label: Color,
    pub confidence_filled: Color,
    pub confidence_empty: Color,
    pub separator: Color,
}

impl AppTheme {
    pub fn default_theme() -> Self {
        Self {
            variant: ThemeVariant::ThreatConnect,
            border: Color::Rgb(255, 122, 79),         // TC_ORANGE
            text: Color::White,                       // TC_WHITE
            input_edit: Color::Rgb(255, 122, 79),     // TC_ORANGE
            title_main: Color::Rgb(255, 122, 79),     // TC_ORANGE
            title_secondary: Color::Rgb(250, 198, 148), // TC_LIGHT_ORANGE
            summary_highlight: Color::Rgb(254, 124, 80), // TC_DARK_ORANGE
            owner_label: Color::Rgb(51, 93, 127),     // TC_DARK_BLUE
            date_label: Color::Rgb(179, 209, 247),    // TC_LIGHT_BLUE
            active_label: Color::Rgb(255, 122, 79),   // TC_ORANGE
            evilness_label: Color::Rgb(163, 76, 0),   // TC_VERY_DARK_ORANGE
            confidence_filled: Color::Rgb(255, 122, 79), // TC_ORANGE
            confidence_empty: Color::White,           // TC_WHITE
            separator: Color::DarkGray,
        }
    }

    pub fn color_pop() -> Self {
        Self {
            variant: ThemeVariant::ColorPop,
            border: Color::Rgb(0, 191, 255),          // popBorder (#00bfff)
            text: Color::Rgb(255, 255, 255),          // popText (#FFFFFF)
            input_edit: Color::Rgb(255, 20, 147),     // popPrimary (#FF1493)
            title_main: Color::Rgb(255, 20, 147),     // popPrimary (#FF1493)
            title_secondary: Color::Rgb(0, 191, 255), // popAccent (#00BFFF)
            summary_highlight: Color::Rgb(255, 20, 147), // popKeyword (#FF1493)
            owner_label: Color::Rgb(0, 191, 255),     // popInfo (#00BFFF)
            date_label: Color::Rgb(129, 124, 121),    // popTextMuted (#817c79)
            active_label: Color::Rgb(0, 255, 0),      // popSuccess (#00FF00)
            evilness_label: Color::Rgb(255, 0, 0),    // popError (#FF0000)
            confidence_filled: Color::Rgb(255, 255, 0), // popWarning (#FFFF00)
            confidence_empty: Color::Rgb(129, 124, 121), // popTextMuted (#817c79)
            separator: Color::Rgb(136, 136, 136),     // popComment (#888888)
        }
    }
}

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
    pub theme: AppTheme,
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
            status_message: String::from("Press 'q' to quit, 'e' to enter search mode, 't' to toggle theme."),
            theme: AppTheme::default_theme(),
        }
    }

    async fn perform_search(&mut self) {
        if self.input.trim().is_empty() {
            return;
        }

        self.status_message = format!("Searching for '{}'...", self.input);

        // Step 1: Initial search to get IDs (Fuzzy match, NO fields)
        // usage of LIKE with wildcards ensures fuzzy matching works reliably
        let tql = format!("summary like \"%{}%\"", self.input);
        let params = vec![
            ("tql", tql.as_str()),
            ("resultStart", "0"),
            ("resultLimit", "100"), // We might need pagination later, but 100 is ok for MVP
            ("sorting", "dateAdded ASC"),
        ];

        match self.client.get::<crate::models::search::SearchResponse>("/indicators", Some(&params)).await {
            Ok(response) => {
                if response.data.is_empty() {
                    self.status_message = format!("No results found for '{}'.", self.input);
                    self.grouped_results.clear();
                    self.stats = SearchStats::default();
                    self.selected_index = 0;
                    self.scroll_offset = 0;
                    return;
                }

                // Step 2: Fetch details for found IDs in parallel chunks
                // We limit to 100 IDs total (from Step 1 limit)
                let basic_indicators = response.data;
                let chunk_size = 20;
                let chunks: Vec<Vec<crate::models::indicator::Indicator>> = basic_indicators
                    .chunks(chunk_size)
                    .map(|chunk| chunk.to_vec())
                    .collect();

                self.status_message = format!("Fetching details for {} indicators ({} chunks)...", basic_indicators.len(), chunks.len());

                let mut handles = Vec::new();

                for chunk in chunks {
                    let client = self.client.clone();
                    handles.push(tokio::spawn(async move {
                        let ids: Vec<String> = chunk.iter().map(|i| i.id.to_string()).collect();
                        let id_list = ids.join(",");
                        let tql_ids = format!("id in ({})", id_list);

                        let params_details = vec![
                            ("tql", tql_ids.as_str()),
                            ("resultLimit", "100"), // ample for the chunk size
                            ("sorting", "dateAdded ASC"), 
                            ("fields", "tags"),
                            ("fields", "associatedGroups"),
                            ("fields", "associatedIndicators"),
                        ];

                        match client.get::<crate::models::search::SearchResponse>("/indicators", Some(&params_details)).await {
                            Ok(detailed_res) => detailed_res.data,
                            Err(_) => chunk, // Fallback to basic indicators on error
                        }
                    }));
                }

                let mut final_indicators = Vec::new();
                for handle in handles {
                    if let Ok(indicators) = handle.await {
                        final_indicators.extend(indicators);
                    }
                }

                self.stats = calculate_stats(&final_indicators);
                self.grouped_results = group_indicators(final_indicators);
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

    fn toggle_theme(&mut self) {
        self.theme = match self.theme.variant {
            ThemeVariant::ThreatConnect => AppTheme::color_pop(),
            ThemeVariant::ColorPop => AppTheme::default_theme(),
        };
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
                        KeyCode::Char('t') => {
                            app_guard.toggle_theme();
                        }
                        KeyCode::Char('q') => {
                            return Ok(());
                        }
                        // Navigation
                        KeyCode::Right | KeyCode::Char('l') => {
                            app_guard.next();
                        }
                        KeyCode::Left | KeyCode::Char('h') => {
                            app_guard.previous();
                        }
                        KeyCode::Down | KeyCode::Char('j') => {
                            app_guard.scroll_down();
                        }
                        KeyCode::Up | KeyCode::Char('k') => {
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
        InputMode::Normal => Style::default().fg(app.theme.text),
        InputMode::Editing => Style::default().fg(app.theme.input_edit),
    };

    let input = Paragraph::new(format!("> {}", app.input.as_str()))
        .style(input_style)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .border_type(BorderType::Rounded)
                .title("Search Indicators")
                .border_style(Style::default().fg(app.theme.title_main))
                .padding(Padding::horizontal(4)),
        );
    f.render_widget(input, header_chunks[0]);

    // Format stats
    let avg_rating = app.stats.avg_rating.map_or("N/A".to_string(), |r| format!("{:.1}", r));
    let avg_conf = app.stats.avg_confidence.map_or("N/A".to_string(), |c| format!("{:.1}%", c));

    let stats_text = vec![
        Line::from(vec![
            Span::styled("Count: ", Style::default().add_modifier(Modifier::BOLD).fg(app.theme.title_main)),
            Span::raw(format!("{}   ", app.stats.total_count)),
            Span::styled("Owners: ", Style::default().add_modifier(Modifier::BOLD).fg(app.theme.title_main)),
            Span::raw(format!("{}   ", app.stats.unique_owners)),
            Span::styled("Avg Evilness: ", Style::default().add_modifier(Modifier::BOLD).fg(app.theme.title_main)),
            Span::raw(format!("{}   ", avg_rating)),
            Span::styled("Avg Conf: ", Style::default().add_modifier(Modifier::BOLD).fg(app.theme.title_main)),
            Span::raw(format!("{}", avg_conf)),
        ]),
        Line::from(vec![
            Span::styled("Active: ", Style::default().add_modifier(Modifier::BOLD).fg(app.theme.title_main)),
            Span::raw(format!("{}   ", app.stats.active_count)),
            Span::styled("False Positives: ", Style::default().add_modifier(Modifier::BOLD).fg(app.theme.title_main)),
            Span::raw(format!("{}   ", app.stats.false_positives)),
        ]),
    ];

    let stats_paragraph = Paragraph::new(stats_text)
        .block(
            Block::default()
                .borders(Borders::TOP)
                .title("Search Stats")
                .border_style(Style::default().fg(app.theme.title_main))
                .padding(Padding::horizontal(4)),
        )
        .style(Style::default().fg(app.theme.text));

    f.render_widget(stats_paragraph, header_chunks[1]);

    // --- Carousel (Main Content) ---

    let carousel_area = chunks[1];
    let block = Block::default()
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .title("Indicator Results")
        .border_style(Style::default().fg(app.theme.border))
        .padding(Padding::new(4, 4, 1, 0)); // Top padding 1

    if app.grouped_results.is_empty() {
        let text = Paragraph::new("No results found. Press 'e' to search.")
            .alignment(Alignment::Center)
            .style(Style::default().fg(app.theme.text))
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
            .border_style(Style::default().fg(app.theme.border))
            .padding(Padding::new(4, 4, 1, 0)); // Top padding 1

        // Content of the card
        let mut content = vec![];

        // Header info for the group
        content.push(Line::from(vec![
            Span::styled("Summary: ", Style::default().fg(app.theme.summary_highlight).add_modifier(Modifier::BOLD)),
            Span::styled(group.summary.clone(), Style::default().add_modifier(Modifier::BOLD).fg(app.theme.text)),
        ]));
        content.push(Line::from(vec![
            Span::styled("Type: ", Style::default().fg(app.theme.title_secondary).add_modifier(Modifier::BOLD)),
            Span::styled(group.indicator_type.clone(), Style::default().fg(app.theme.text)),
        ]));
        // Removed empty line before divider
        let divider_len = carousel_area.width.saturating_sub(10) as usize; // width - borders(2) - padding(8)
        content.push(Line::from(Span::styled("─".repeat(divider_len), Style::default().fg(app.theme.text))));

        // List all indicators
        for (idx, indicator) in group.indicators.iter().enumerate() {
            if idx > 0 {
                content.push(Line::from(""));
                content.push(Line::from(Span::styled("- - - - -", Style::default().fg(app.theme.separator))));
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
                Span::styled("Owner: ", Style::default().fg(app.theme.owner_label).add_modifier(Modifier::BOLD)),
                Span::styled(indicator.owner_name.clone(), Style::default().fg(app.theme.text)),
                Span::styled(" | ", Style::default().fg(app.theme.text)),
                Span::styled("Active: ", Style::default().fg(app.theme.active_label).add_modifier(Modifier::BOLD)),
                Span::styled(if indicator.active { "Yes" } else { "No" }, Style::default().fg(app.theme.text)),
            ]));

            // Line 2
            content.push(Line::from(vec![
                Span::styled("Added: ", Style::default().fg(app.theme.date_label)),
                Span::styled(indicator.date_added.format("%Y-%m-%d %H:%M").to_string(), Style::default().fg(app.theme.text)),
                Span::styled(" | ", Style::default().fg(app.theme.text)),
                Span::styled("Modified: ", Style::default().fg(app.theme.date_label)),
                Span::styled(indicator.last_modified.format("%Y-%m-%d %H:%M").to_string(), Style::default().fg(app.theme.text)),
            ]));

            // Line 3: Evilness
            content.push(Line::from(vec![
                Span::styled("Evilness: ", Style::default().fg(app.theme.evilness_label)),
                Span::styled(format!("{} ({:.1})", rating_skulls, indicator.rating), Style::default().fg(app.theme.text)),
            ]));

            // Line 4: Confidence Bar
            let conf_val = indicator.confidence as u32; // 0-100
            let filled_count = (conf_val as f32 / 10.0).round() as usize;
            let filled_count = filled_count.clamp(0, 10);
            let empty_count = 10 - filled_count;

            let filled_bar = "-".repeat(filled_count);
            let empty_bar = "-".repeat(empty_count);

            content.push(Line::from(vec![
                Span::styled("Confidence: ", Style::default().fg(app.theme.title_main)),
                Span::styled(format!("{}% [", conf_val), Style::default().fg(app.theme.text)),
                Span::styled(filled_bar, Style::default().fg(app.theme.confidence_filled)),
                Span::styled(empty_bar, Style::default().fg(app.theme.confidence_empty)),
                Span::styled("]", Style::default().fg(app.theme.text)),
            ]));

            if let Some(desc) = &indicator.description {
                if !desc.is_empty() {
                    content.push(Line::from(Span::styled("Description:", Style::default().add_modifier(Modifier::UNDERLINED).fg(app.theme.text))));
                    content.push(Line::from(Span::styled(desc.clone(), Style::default().fg(app.theme.text))));
                }
            }

            // Tags
            if !indicator.tags.is_empty() {
                // Empty line break between description (or previous field) and tags
                content.push(Line::from(""));

                let tags_str: String = indicator.tags.iter()
                    .map(|t| t.name.clone())
                    .collect::<Vec<String>>()
                    .join(" | ");

                content.push(Line::from(vec![
                    Span::styled("Tags: ", Style::default().fg(app.theme.title_secondary).add_modifier(Modifier::BOLD)),
                    Span::styled(tags_str, Style::default().fg(app.theme.text)),
                ]));
            }

            // Associated Groups
            if !indicator.associated_groups.is_empty() {
                content.push(Line::from(Span::styled("Associated Groups:", Style::default().fg(app.theme.title_secondary).add_modifier(Modifier::BOLD))));
                for group in &indicator.associated_groups {
                    let name = group.name.clone().or(group.summary.clone()).unwrap_or_else(|| "Unknown".to_string());
                    content.push(Line::from(vec![
                        Span::styled("  • ", Style::default().fg(app.theme.text)),
                        Span::styled(name, Style::default().fg(app.theme.text)),
                    ]));
                }
            }

            // Associated Indicators
            if !indicator.associated_indicators.is_empty() {
                content.push(Line::from(Span::styled("Associated Indicators:", Style::default().fg(app.theme.title_secondary).add_modifier(Modifier::BOLD))));
                for assoc_ind in &indicator.associated_indicators {
                    let name = assoc_ind.summary.clone().or(assoc_ind.name.clone()).unwrap_or_else(|| "Unknown".to_string());
                    content.push(Line::from(vec![
                        Span::styled("  • ", Style::default().fg(app.theme.text)),
                        Span::styled(name, Style::default().fg(app.theme.text)),
                    ]));
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
            Span::styled(" ←/→ ", Style::default().fg(app.theme.title_main)),
            Span::styled("Next/Prev Group  |  ", Style::default().fg(app.theme.text)),
            Span::styled(" ↑/↓ ", Style::default().fg(app.theme.title_main)),
            Span::styled("Scroll  |  ", Style::default().fg(app.theme.text)),
            Span::styled(" e ", Style::default().fg(app.theme.title_main)),
            Span::styled("Search  |  ", Style::default().fg(app.theme.text)),
            Span::styled(" q ", Style::default().fg(app.theme.title_main)),
            Span::styled("Quit", Style::default().fg(app.theme.text)),
        ]),
        Line::from(Span::styled(app.status_message.clone(), Style::default().fg(app.theme.text))),
    ];
    let footer = Paragraph::new(footer_text)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .border_type(BorderType::Rounded)
                .title("Navigation")
                .border_style(Style::default().fg(app.theme.border))
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
