# ThreatConnect CLI - Modular Architecture

## Overview

This document defines the modular architecture for the ThreatConnect CLI modernization, designed to enable parallel development by multiple teams/agents with minimal overlap and clear integration points.

## Architecture Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Dependency Inversion**: Modules depend on interfaces, not implementations
3. **Clear Contracts**: All module boundaries have explicit interfaces
4. **Independent Testing**: Each module can be tested in isolation with mocks
5. **Minimal Coupling**: Modules communicate through well-defined APIs only

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Main Application                        │
│                    (tc_tui/app.py)                          │
└────────────┬────────────────────────────────────────────────┘
             │
             ├──────────────────────────────────────────────────┐
             │                                                  │
    ┌────────▼─────────┐                            ┌──────────▼─────────┐
    │   UI Layer       │                            │   Business Logic   │
    │                  │                            │                    │
    │ - Screens        │◄───────────────────────────┤ - Search Engine    │
    │ - Widgets        │      Display Data          │ - State Manager    │
    │ - Layout         │                            │ - Query Builder    │
    └────────┬─────────┘                            └──────────┬─────────┘
             │                                                  │
             │                                                  │
    ┌────────▼─────────┐                            ┌──────────▼─────────┐
    │  Widget Library  │                            │   Data Models      │
    │                  │                            │                    │
    │ - SearchInput    │                            │ - Indicator        │
    │ - ResultsTable   │◄───────────────────────────┤ - Group            │
    │ - DetailView     │      Model Objects         │ - SearchResult     │
    │ - StatusBar      │                            │ - Association      │
    └──────────────────┘                            └──────────┬─────────┘
                                                                │
                                                                │
                                                    ┌──────────▼─────────┐
                                                    │   API Client       │
                                                    │                    │
                                                    │ - Auth Handler     │
                                                    │ - HTTP Client      │
                                                    │ - Indicators API   │
                                                    │ - Groups API       │
                                                    └──────────┬─────────┘
                                                                │
                                                                │
    ┌───────────────────────────────────────────────────────────▼─────┐
    │                  Configuration & Utils                          │
    │                                                                  │
    │  - Config Manager  - Icon Mapper  - Formatters  - Cache         │
    └──────────────────────────────────────────────────────────────────┘
```

## Module Breakdown

### Layer 1: Data & API (No UI Dependencies)

#### Module 1: Data Models (`tc_tui/models/`)
**Purpose**: Define all data structures using Pydantic

**Responsibilities**:
- Define Indicator, Group, Tag, Attribute models
- Define SearchResult and pagination models
- Validation logic
- Type definitions

**Dependencies**: None (only Pydantic)

**Key Files**:
- `models/__init__.py` - Public API exports
- `models/indicator.py` - Indicator models
- `models/group.py` - Group models
- `models/common.py` - Shared models (Tag, Attribute, etc.)
- `models/search.py` - Search request/response models

**Interface Contract**:
```python
# All models expose Pydantic models with validation
class Indicator(BaseModel):
    id: int
    type: str
    summary: str
    rating: float
    confidence: int
    # ... etc

class SearchResult(BaseModel):
    data: List[Union[Indicator, Group]]
    total: int
    current_page: int
    total_pages: int
```

---

#### Module 2: API Client (`tc_tui/api/`)
**Purpose**: Handle all ThreatConnect API communication

**Responsibilities**:
- HMAC authentication
- HTTP requests
- Response parsing
- Error handling
- Rate limiting

**Dependencies**:
- `models/` for request/response types
- `config/` for credentials

**Key Files**:
- `api/__init__.py` - Public API exports
- `api/client.py` - Base HTTP client with auth
- `api/auth.py` - Authentication logic
- `api/indicators.py` - Indicator endpoints
- `api/groups.py` - Group endpoints
- `api/exceptions.py` - API exceptions

**Interface Contract**:
```python
class ThreatConnectClient:
    async def search_indicators(
        self,
        tql: str = None,
        summary: str = None,
        page: int = 0,
        limit: int = 100
    ) -> SearchResult:
        """Search indicators with TQL or summary"""

    async def get_indicator_details(
        self,
        indicator_id: int,
        include_tags: bool = True,
        include_attributes: bool = True
    ) -> Indicator:
        """Get full indicator details"""

    async def get_indicator_associations(
        self,
        indicator_id: int
    ) -> List[Association]:
        """Get associated groups and indicators"""
```

---

#### Module 3: Configuration (`tc_tui/config/`)
**Purpose**: Manage configuration and credentials

**Responsibilities**:
- Load/save TOML config
- Environment variable handling
- Default settings
- Config validation

**Dependencies**: None (only standard library + platformdirs)

**Key Files**:
- `config/__init__.py` - Public API exports
- `config/manager.py` - Config loading/saving
- `config/models.py` - Config data models
- `config/defaults.py` - Default values

**Interface Contract**:
```python
class ConfigManager:
    def load() -> AppConfig:
        """Load config from file or create default"""

    def save(config: AppConfig) -> None:
        """Save config to file"""

    def get_api_credentials() -> tuple[str, str, str]:
        """Returns (access_id, secret_key, instance)"""

@dataclass
class AppConfig:
    api: APIConfig
    ui: UIConfig
    keybindings: KeyBindings
    defaults: Defaults
```

---

#### Module 4: Utilities (`tc_tui/utils/`)
**Purpose**: Shared utility functions

**Responsibilities**:
- Icon mapping for types
- Data formatting
- Date/time utilities
- Text processing

**Dependencies**:
- `models/` for type definitions

**Key Files**:
- `utils/__init__.py` - Public API exports
- `utils/icons.py` - Icon mapping
- `utils/formatters.py` - Data formatters
- `utils/validators.py` - Input validation
- `utils/cache.py` - Caching utilities

**Interface Contract**:
```python
class IconMapper:
    @staticmethod
    def get_indicator_icon(indicator_type: str) -> str:
        """Return emoji/icon for indicator type"""

    @staticmethod
    def get_group_icon(group_type: str) -> str:
        """Return emoji/icon for group type"""

class Formatters:
    @staticmethod
    def format_date(date_str: str) -> str:
        """Format ISO date to readable format"""

    @staticmethod
    def format_rating(rating: float) -> str:
        """Format rating as stars"""
```

---

### Layer 2: Business Logic (No Direct UI)

#### Module 5: Search Engine (`tc_tui/search/`)
**Purpose**: Handle search logic and query building

**Responsibilities**:
- TQL query construction
- Indicator type detection
- Search history management
- Query validation

**Dependencies**:
- `api/` for executing searches
- `models/` for data types

**Key Files**:
- `search/__init__.py` - Public API exports
- `search/engine.py` - Search orchestration
- `search/tql_builder.py` - TQL query construction
- `search/detector.py` - Indicator type detection
- `search/history.py` - Search history

**Interface Contract**:
```python
class SearchEngine:
    async def search(
        self,
        query: str,
        search_type: SearchType,  # INDICATOR, GROUP, BOTH
        filters: Optional[SearchFilters] = None
    ) -> SearchResult:
        """Execute search and return results"""

    def detect_indicator_type(self, value: str) -> Optional[str]:
        """Auto-detect indicator type from value"""

    def build_tql_query(
        self,
        value: str = None,
        indicator_type: str = None,
        filters: SearchFilters = None
    ) -> str:
        """Build TQL query from parameters"""
```

---

#### Module 6: State Manager (`tc_tui/state/`)
**Purpose**: Manage application state

**Responsibilities**:
- Current search results
- Selected item
- Navigation history
- UI state (active panel, etc.)

**Dependencies**:
- `models/` for data types

**Key Files**:
- `state/__init__.py` - Public API exports
- `state/manager.py` - State management
- `state/models.py` - State data models
- `state/events.py` - State change events

**Interface Contract**:
```python
class StateManager:
    # Observable state
    current_results: Observable[SearchResult]
    selected_item: Observable[Union[Indicator, Group, None]]
    navigation_history: List[NavigationState]

    def update_results(self, results: SearchResult) -> None:
        """Update search results"""

    def select_item(self, index: int) -> None:
        """Select item by index"""

    def navigate_back(self) -> None:
        """Go back in navigation history"""
```

---

### Layer 3: UI Components (Reusable Widgets)

#### Module 7: Widget Library (`tc_tui/widgets/`)
**Purpose**: Reusable UI components

**Responsibilities**:
- Individual widget implementations
- Widget-specific logic
- Event handling
- Styling

**Dependencies**:
- `models/` for data types
- `utils/` for formatting
- Textual framework

**Key Files**:
- `widgets/__init__.py` - Public API exports
- `widgets/search_input.py` - Search input widget
- `widgets/results_table.py` - Results table widget
- `widgets/detail_view.py` - Detail panel widget
- `widgets/status_bar.py` - Status bar widget
- `widgets/filter_panel.py` - Filter panel widget
- `widgets/help_modal.py` - Help modal widget

**Interface Contract**:
```python
class SearchInput(Widget):
    """Search input with type selector"""

    class Submitted(Message):
        """Posted when search is submitted"""
        def __init__(self, query: str, search_type: SearchType):
            ...

    def on_mount(self) -> None:
        """Setup widget"""

    def on_key(self, event: Key) -> None:
        """Handle key events"""

class ResultsTable(Widget):
    """Table displaying search results"""

    class ItemSelected(Message):
        """Posted when item is selected"""
        def __init__(self, item: Union[Indicator, Group], index: int):
            ...

    def update_results(self, results: SearchResult) -> None:
        """Update table with new results"""

    def select_row(self, index: int) -> None:
        """Select row by index"""

class DetailView(Widget):
    """Panel showing item details"""

    async def set_item(
        self,
        item: Union[Indicator, Group],
        include_associations: bool = True
    ) -> None:
        """Display item details"""
```

---

### Layer 4: Application Screens

#### Module 8: Screens (`tc_tui/screens/`)
**Purpose**: Complete screen layouts

**Responsibilities**:
- Compose widgets into screens
- Screen-level logic
- Screen navigation

**Dependencies**:
- `widgets/` for UI components
- `state/` for state management
- `search/` for search operations

**Key Files**:
- `screens/__init__.py` - Public API exports
- `screens/main_screen.py` - Main search screen
- `screens/help_screen.py` - Help screen
- `screens/settings_screen.py` - Settings screen

**Interface Contract**:
```python
class MainScreen(Screen):
    """Main application screen"""

    def compose(self) -> ComposeResult:
        """Compose the screen layout"""
        yield SearchInput(id="search")
        yield ResultsTable(id="results")
        yield DetailView(id="details")
        yield StatusBar(id="status")

    async def on_search_input_submitted(
        self,
        message: SearchInput.Submitted
    ) -> None:
        """Handle search submission"""

    async def on_results_table_item_selected(
        self,
        message: ResultsTable.ItemSelected
    ) -> None:
        """Handle item selection"""
```

---

### Layer 5: Main Application

#### Module 9: Main App (`tc_tui/`)
**Purpose**: Application entry point and orchestration

**Responsibilities**:
- Application initialization
- Screen management
- Global keybindings
- Error handling

**Dependencies**: All other modules

**Key Files**:
- `app.py` - Main Textual app
- `__main__.py` - CLI entry point

**Interface Contract**:
```python
class ThreatConnectApp(App):
    """Main Textual application"""

    CSS_PATH = "app.css"
    SCREENS = {
        "main": MainScreen,
        "help": HelpScreen,
        "settings": SettingsScreen
    }

    def on_mount(self) -> None:
        """Initialize app"""

    def action_quit(self) -> None:
        """Quit application"""

    def action_show_help(self) -> None:
        """Show help screen"""
```

---

## Integration Contracts

### Contract 1: API Client ↔ Models
- API client accepts and returns Pydantic models
- All validation happens in models
- API client handles serialization/deserialization

### Contract 2: Search Engine ↔ API Client
- Search engine uses API client for all network operations
- Search engine never directly imports `requests`
- API client returns typed models

### Contract 3: Widgets ↔ Models
- Widgets receive models as props
- Widgets emit events, never modify models directly
- All formatting happens in widgets/utils

### Contract 4: State Manager ↔ UI
- State manager is the single source of truth
- UI components observe state changes
- UI sends actions to state manager

### Contract 5: Screens ↔ Widgets
- Screens compose widgets
- Widgets are reusable and self-contained
- Communication via Textual message passing

## Testing Strategy

### Module 1: Data Models
- **Test Type**: Unit tests
- **Mocking**: None needed
- **Focus**: Validation, serialization

### Module 2: API Client
- **Test Type**: Integration tests with mocked HTTP
- **Mocking**: Mock `requests` library
- **Focus**: Auth, request formation, error handling

### Module 3: Configuration
- **Test Type**: Unit tests
- **Mocking**: Mock filesystem
- **Focus**: Loading, saving, validation

### Module 4: Utilities
- **Test Type**: Unit tests
- **Mocking**: None needed
- **Focus**: Formatting, icon mapping

### Module 5: Search Engine
- **Test Type**: Unit tests with mocked API
- **Mocking**: Mock API client
- **Focus**: TQL building, type detection

### Module 6: State Manager
- **Test Type**: Unit tests
- **Mocking**: None needed
- **Focus**: State updates, events

### Module 7: Widget Library
- **Test Type**: UI tests with Textual's test harness
- **Mocking**: Mock data models
- **Focus**: Rendering, interactions

### Module 8: Screens
- **Test Type**: UI tests with Textual's test harness
- **Mocking**: Mock widgets, state
- **Focus**: Layout, navigation

### Module 9: Main App
- **Test Type**: End-to-end tests
- **Mocking**: Mock API for integration
- **Focus**: Full workflows

## Dependency Graph

```
Level 0 (No Dependencies):
  - models/
  - config/

Level 1 (Depends on Level 0):
  - utils/ (depends on models/)
  - api/ (depends on models/, config/)

Level 2 (Depends on Level 0-1):
  - search/ (depends on api/, models/)
  - state/ (depends on models/)

Level 3 (Depends on Level 0-2):
  - widgets/ (depends on models/, utils/, Textual)

Level 4 (Depends on Level 0-3):
  - screens/ (depends on widgets/, state/, search/)

Level 5 (Depends on All):
  - app.py (depends on screens/, config/)
```

## File Organization

```
tc_tui/
├── __init__.py
├── __main__.py              # Entry point
├── app.py                   # Main Textual app (Module 9)
├── app.css                  # Global styles
│
├── models/                  # Module 1: Data Models
│   ├── __init__.py
│   ├── indicator.py
│   ├── group.py
│   ├── common.py
│   └── search.py
│
├── api/                     # Module 2: API Client
│   ├── __init__.py
│   ├── client.py
│   ├── auth.py
│   ├── indicators.py
│   ├── groups.py
│   └── exceptions.py
│
├── config/                  # Module 3: Configuration
│   ├── __init__.py
│   ├── manager.py
│   ├── models.py
│   └── defaults.py
│
├── utils/                   # Module 4: Utilities
│   ├── __init__.py
│   ├── icons.py
│   ├── formatters.py
│   ├── validators.py
│   └── cache.py
│
├── search/                  # Module 5: Search Engine
│   ├── __init__.py
│   ├── engine.py
│   ├── tql_builder.py
│   ├── detector.py
│   └── history.py
│
├── state/                   # Module 6: State Manager
│   ├── __init__.py
│   ├── manager.py
│   ├── models.py
│   └── events.py
│
├── widgets/                 # Module 7: Widget Library
│   ├── __init__.py
│   ├── search_input.py
│   ├── results_table.py
│   ├── detail_view.py
│   ├── status_bar.py
│   ├── filter_panel.py
│   └── help_modal.py
│
└── screens/                 # Module 8: Screens
    ├── __init__.py
    ├── main_screen.py
    ├── help_screen.py
    └── settings_screen.py
```

## Development Workflow

### Phase 1: Foundation (Parallel)
All Level 0-1 modules can be developed simultaneously:
- Agent A: Module 1 (Models)
- Agent B: Module 2 (API Client)
- Agent C: Module 3 (Configuration)
- Agent D: Module 4 (Utilities)

### Phase 2: Business Logic (Parallel)
All Level 2 modules can be developed simultaneously:
- Agent A: Module 5 (Search Engine)
- Agent B: Module 6 (State Manager)

### Phase 3: UI Components (Parallel)
Module 7 widgets can be split among agents:
- Agent A: SearchInput + FilterPanel
- Agent B: ResultsTable
- Agent C: DetailView
- Agent D: StatusBar + HelpModal

### Phase 4: Integration (Sequential)
- Agent A: Module 8 (Screens) - requires widgets
- Agent B: Module 9 (Main App) - requires screens

## Mock Data for Independent Development

Create `tests/fixtures/` with mock data:

```python
# tests/fixtures/indicators.py
MOCK_INDICATOR = {
    "id": 12345,
    "type": "Address",
    "summary": "192.168.1.1",
    "rating": 3.5,
    "confidence": 85,
    # ... full mock data
}

MOCK_SEARCH_RESULT = {
    "data": [MOCK_INDICATOR, ...],
    "total": 150,
    "current_page": 1,
    "total_pages": 2
}
```

All UI developers use these fixtures for testing without API dependency.

## Version Control Strategy

### Branch Naming
- `module/1-data-models` - Data models work
- `module/2-api-client` - API client work
- `module/3-config` - Configuration work
- `module/7-widget-search-input` - Specific widget work

### Integration Branch
- `integration/phase-1` - Integration of Phase 1 modules
- `integration/phase-2` - Integration of Phase 2 modules

### Pull Request Guidelines
1. Each module has clear acceptance criteria
2. All tests pass before merge
3. Code review focuses on interface adherence
4. Integration tests run on integration branches

## Success Criteria

Each module is complete when:
- ✅ All public interfaces implemented
- ✅ Unit tests pass with >80% coverage
- ✅ Type hints on all public functions
- ✅ Docstrings on all public classes/functions
- ✅ Integration contract verified
- ✅ Mock data provided for dependent modules

---

**Document Version**: 1.0
**Last Updated**: 2025-11-22
