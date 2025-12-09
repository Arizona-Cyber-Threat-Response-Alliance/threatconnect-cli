# Project Context

## Purpose
The ThreatConnect CLI is a modern terminal user interface (TUI) for interacting with the ThreatConnect threat intelligence platform. It enables security analysts to search, view, and manage indicators and threat data through an intuitive terminal interface. The project is currently being rewritten in **Rust** to utilize the **Ratatui** framework for a more robust and performant user experience.

## Tech Stack
- **Rust** - Primary language (2021/2024 edition)
- **Ratatui** - Modern TUI framework for rich terminal interfaces
- **Tokio** - Async runtime for I/O operations
- **Reqwest** - HTTP client for API communication
- **Serde** - Serialization/Deserialization framework
- **Crossterm** - Terminal manipulation and input handling

## Project Conventions

### Code Style
- **Rustfmt**: Standard Rust formatting
- **Clippy**: Standard Rust linter
- **Async/Await**: All I/O operations use async/await patterns
- **Error Handling**: Use `anyhow` or `thiserror` for error management
- **Structs**: Data models using Serde for JSON handling

### Architecture Patterns
- **The Elm Architecture / MVI**: Model-View-Update pattern common in Rust TUIs
- **Repository Pattern**: API client abstracts data access
- **State Management**: Centralized application state
- **Async API**: Non-blocking API calls

### Git Workflow
- **Feature Branches**: `module/{number}-{name}` pattern for modular development
- **Integration Branches**: `integration/phase-{n}` for combining modules
- **Pull Requests**: Required for all changes with code review
- **Commit Messages**: Conventional commits with scope (e.g., `feat(models): add indicator validation`)

## Domain Context
This is a cybersecurity threat intelligence tool for the ThreatConnect platform. Key domain concepts:
- **Indicators**: IOCs like IPs, domains, hashes, email addresses
- **Groups**: Threat reports, campaigns, malware, attack patterns
- **TQL**: ThreatConnect Query Language for complex searches
- **Attributes**: Additional metadata fields on indicators/groups
- **Tags**: Classification labels for threat data
- **Associations**: Relationships between indicators and groups
- **Rating/Confidence**: Scoring system for threat data reliability

## Important Constraints
- **API Rate Limits**: Must respect ThreatConnect API rate limiting
- **Security**: Never log or expose API credentials
- **Performance**: Handle large datasets with pagination
- **Compatibility**: Support modern terminals with UTF-8 support
- **Offline Mode**: Graceful degradation when API unavailable

## External Dependencies
- **ThreatConnect API**: Primary data source with HMAC authentication
- **Environment Variables**: API credentials (TC_ACCESS_ID, TC_SECRET_KEY, TC_INSTANCE)
- **Network Connectivity**: Internet access for API communication
