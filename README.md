# ThreatConnect TUI

![ThreatConnect TUI](new_tui_tc.png)

A modern, terminal-based user interface for interacting with the ThreatConnect Platform. This tool provides a keyboard-centric, efficient way to search indicators, view details, and manage your ThreatConnect data directly from your terminal.

## Features

*   **Fast & Efficient**: Built in Rust for performance and low resource usage.
*   **Keyboard Navigation**: Vim-like keybindings for rapid interaction.
*   **Detailed Views**: Inspect indicators, attributes, tags, and associations.
*   **Search**: Powerful search capabilities to find what you need quickly.

## Prerequisites

*   **Rust**: You need to have Rust and Cargo installed. You can install them via [rustup](https://rustup.rs/).
*   **ThreatConnect API Credentials**: You need an API Access ID and Secret Key from your ThreatConnect instance.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Arizona-Cyber-Threat-Response-Alliance/threatconnect-tui.git
    cd threatconnect-tui
    ```

2.  **Configure Credentials:**

    Copy the example environment file and add your credentials:

    ```bash
    cp .env.example .env
    ```

    Edit `.env` with your preferred editor and fill in your details:

    ```env
    TC_ACCESS_ID=your_access_id
    TC_SECRET_KEY=your_secret_key
    TC_INSTANCE=your_instance_url (e.g., https://api.threatconnect.com)
    ```

## Usage

### Using Cargo (Recommended)

To run the application directly with Cargo:

```bash
cargo run
```

### Using NPM

If you prefer using NPM scripts (e.g., in a mixed environment), we provide a wrapper:

```bash
npm install
npm start
```

## Keybindings

*   **Navigation**: `h`, `j`, `k`, `l` (Left, Down, Up, Right) or Arrow Keys.
*   **Select/Enter**: `Enter`.
*   **Back/Escape**: `Esc`.
*   **Quit**: `q` or `Ctrl+c`.
*   **Theme Toggle**: `t`.

## Development

The project is structured as a standard Rust binary crate.

*   **Run Tests**: `cargo test`
*   **Build Release**: `cargo build --release`

## Legacy Python Tool

The previous Python-based CLI tool has been moved to the `legacy/` directory.

## License

[License Information]
