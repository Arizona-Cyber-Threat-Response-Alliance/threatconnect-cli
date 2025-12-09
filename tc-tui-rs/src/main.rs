mod api;
mod models;
mod tui;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tui::run_app().await?;
    Ok(())
}
