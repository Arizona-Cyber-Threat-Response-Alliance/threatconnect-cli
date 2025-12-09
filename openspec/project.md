# Project Context

## Purpose
The ThreatConnect CLI is a modern terminal user interface (TUI) for interacting with the ThreatConnect threat intelligence platform. It enables security analysts to search, view, and manage indicators and threat data through an intuitive terminal interface. The project is undergoing modernization from a simple script-based tool to a modular, async TUI application built with Textual.

## Tech Stack
- **Python 3.8+** - Primary language
- **Textual** - Modern TUI framework for rich terminal interfaces
- **Pydantic** - Data validation and modeling
- **Requests** - HTTP client for API communication
- **Rich** - Terminal formatting and styling
- **pytest** - Testing framework with coverage
- **TOML** - Configuration file format
- **Platformdirs** - Cross-platform config directory handling

## Project Conventions

### Code Style
- **Type Hints**: All public functions and classes must have type hints
- **Docstrings**: Google-style docstrings on all public APIs
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Imports**: Organized imports (stdlib, third-party, local) with isort formatting
- **Async/Await**: All I/O operations use async/await patterns
- **Pydantic Models**: All data structures use Pydantic for validation

### Architecture Patterns
- **Modular Architecture**: 9-layer dependency hierarchy with clear separation of concerns
- **Dependency Inversion**: Modules depend on interfaces, not implementations
- **Event-Driven UI**: Textual message passing for widget communication
- **Repository Pattern**: API client abstracts data access
- **Observer Pattern**: State manager with observable state changes
- **Factory Pattern**: Widget creation and configuration

### Testing Strategy
- **Unit Tests**: pytest with >80% coverage requirement
- **Mocking**: Use pytest-mock for external dependencies
- **UI Tests**: Textual's test harness for widget testing
- **Integration Tests**: End-to-end workflows with mocked API
- **Fixtures**: Comprehensive mock data in `tests/fixtures/`
- **Test Organization**: Mirror source structure in tests/

### Git Workflow
- **Feature Branches**: `module/{number}-{name}` pattern for modular development
- **Integration Branches**: `integration/phase-{n}` for combining modules
- **Pull Requests**: Required for all changes with code review
- **Commit Messages**: Conventional commits with scope (e.g., `feat(models): add indicator validation`)
- **Version Control**: Semantic versioning with automated releases

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
- **Performance**: Handle large datasets with pagination and caching
- **Compatibility**: Support Python 3.8+ and multiple terminal types
- **Offline Mode**: Graceful degradation when API unavailable
- **Data Privacy**: Sanitize sensitive data in logs and displays

## External Dependencies
- **ThreatConnect API**: Primary data source with HMAC authentication
- **Environment Variables**: API credentials (TC_ACCESS_ID, TC_SECRET_KEY, TC_INSTANCE)
- **Configuration Files**: TOML format in user config directory
- **Terminal Capabilities**: Requires modern terminal with UTF-8 support
- **Network Connectivity**: Internet access for API communication
