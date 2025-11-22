# ThreatConnect CLI Modernization Plan

## Executive Summary

This document outlines a comprehensive multi-phase plan to modernize the ThreatConnect CLI from a basic command-line tool into a polished, feature-rich Terminal User Interface (TUI) application. The modernization will leverage the Textual framework with Rich library integration to create a professional, keyboard-driven interface supporting both Indicators and Groups with advanced navigation and search capabilities.

## Technology Stack Decision: Python + Textual

### Rationale

After evaluating both Python (Textual) and Go (Bubble Tea) frameworks, **Python with Textual** is recommended for the following reasons:

1. **Existing Codebase**: Current implementation is Python-based with established ThreatConnect API integration
2. **AI-Friendly Development**: Textual has excellent documentation and clear patterns, making it ideal for AI-assisted development
3. **Rich Ecosystem**: Seamless integration with Rich library for advanced text formatting and styling
4. **Rapid Development**: CSS-like styling system enables quick UI iterations
5. **Live Reload**: Built-in dev mode with live CSS/layout updates (`textual run --dev`)
6. **Lower Learning Curve**: More accessible for contributors compared to Go's Elm Architecture pattern
7. **Mature Framework**: Textual reached v1.0 status and is production-ready

### Alternative Considered

**Go + Bubble Tea** was evaluated but not selected because:
- Requires complete rewrite of existing Python codebase
- Steeper learning curve with functional programming paradigm
- Less out-of-the-box UI components (requires more custom implementation)
- Existing Python API integration code would be lost

## Reference Documentation

### TUI Framework Resources
- [Textual Official Documentation](https://textual.textualize.io/)
- [7 Things I've Learned Building a Modern TUI Framework](https://www.textualize.io/blog/7-things-ive-learned-building-a-modern-tui-framework/)
- [Python Textual: Build Beautiful UIs in the Terminal – Real Python](https://realpython.com/python-textual/)
- [8 TUI Patterns to Turn Python Scripts Into Apps](https://medium.com/@Nexumo_/8-tui-patterns-to-turn-python-scripts-into-apps-ce6f964d3b6f)
- [Textual Definitive Guide](https://dev.to/wiseai/textual-the-definitive-guide-part-1-1i0p)

### ThreatConnect API Documentation
- [ThreatConnect Query Language (TQL)](https://knowledge.threatconnect.com/docs/threatconnect-query-language-tql)
- [Filter Results With TQL - API v3](https://docs.threatconnect.com/en/latest/rest_api/v3/filter_results.html)
- [Indicators API v3](https://docs.threatconnect.com/en/latest/rest_api/v3/indicators/indicators.html)
- [Groups API v3](https://docs.threatconnect.com/en/latest/rest_api/v3/groups/groups.html)
- [Constructing Query Expressions](https://knowledge.threatconnect.com/docs/constructing-query-expressions)
- [TQL Operators and Parameters](https://knowledge.threatconnect.com/docs/tql-operators-and-parameters)
- [API Overview - Pagination](https://docs.threatconnect.com/en/latest/rest_api/overview.html)

### TUI Design Best Practices
- [Awesome TUIs - Project Examples](https://github.com/rothgar/awesome-tuis)
- [Terminal Trove - TUI Tools](https://terminaltrove.com/categories/tui/)

## Current State Analysis

### Existing Features
- Basic CLI with text input for indicators
- TQL query construction for indicator searches
- HMAC-SHA256 authentication with ThreatConnect API v3
- Colorama-based colorized output
- Support for multiple indicator types (IPv4, IPv6, Host, Email, URL, MD5, SHA-1, SHA-256, ASN, etc.)
- Regex-based indicator type detection

### Current Limitations
- No Groups support
- No pagination handling
- No navigation through results
- No visual organization of data
- No tags/attributes retrieval
- Limited error handling
- No configuration management
- Hard-coded instance name input

## Supported ThreatConnect Data Types

### Indicator Types
Based on [ThreatConnect API Documentation](https://docs.threatconnect.com/en/latest/rest_api/v3/indicators/indicators.html):

| Type | API Name | Icon | Description |
|------|----------|------|-------------|
| IPv4/IPv6 | Address | 🌐 | IP addresses |
| Hostname | Host | 🖥️ | Domain names and hostnames |
| Email Address | EmailAddress | 📧 | Email addresses |
| URL | URL | 🔗 | Web URLs |
| File Hash (MD5/SHA1/SHA256) | File | 📄 | File hashes |
| ASN | ASN | 🔢 | Autonomous System Numbers |
| CIDR | CIDR | 📍 | Network ranges |
| Mutex | Mutex | 🔒 | Mutex names |
| Registry Key | RegistryKey | 🗝️ | Windows registry keys |
| User Agent | UserAgent | 🤖 | Browser user agents |
| Custom Indicators | (varies) | ⚙️ | Instance-specific types |

### Group Types
Based on [ThreatConnect API Documentation](https://docs.threatconnect.com/en/latest/rest_api/v3/groups/groups.html):

| Type | API Name | Icon | Description |
|------|----------|------|-------------|
| Adversary | Adversary | 💀 | Threat actors |
| Campaign | Campaign | 🎯 | Attack campaigns |
| Document | Document | 📋 | Intelligence documents |
| Email | Email | ✉️ | Email messages |
| Event | Event | 📅 | Security events |
| Incident | Incident | 🚨 | Security incidents |
| Intrusion Set | IntrusionSet | 🔴 | Intrusion sets |
| Report | Report | 📊 | Intelligence reports |
| Signature | Signature | ✍️ | Detection signatures |
| Threat | Threat | ⚠️ | Threat intelligence |

## Multi-Phase Implementation Plan

---

## Phase 1: Foundation & Architecture (Weeks 1-2)

### Objectives
- Set up Textual framework with proper project structure
- Implement configuration management
- Create base API client with authentication
- Establish UI component architecture

### Tasks

#### 1.1 Project Structure Setup
```
threatconnect-cli/
├── tc_tui/
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── app.py               # Main Textual app
│   ├── config.py            # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── client.py        # Base API client
│   │   ├── auth.py          # Authentication (HMAC)
│   │   ├── indicators.py    # Indicator API methods
│   │   └── groups.py        # Group API methods
│   ├── models/
│   │   ├── __init__.py
│   │   ├── indicator.py     # Indicator data models
│   │   └── group.py         # Group data models
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── search_input.py  # Search input widget
│   │   ├── results_table.py # Results display
│   │   ├── detail_view.py   # Detail panel
│   │   └── status_bar.py    # Status/info bar
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── main_screen.py   # Main UI screen
│   │   └── help_screen.py   # Help/keybindings
│   └── utils/
│       ├── __init__.py
│       ├── icons.py         # Icon mappings
│       └── formatters.py    # Data formatters
├── tests/
├── .env.example
├── requirements.txt
├── setup.py
├── pyproject.toml
└── README.md
```

#### 1.2 Dependencies Installation
Update `requirements.txt`:
```
textual>=0.90.0
rich>=13.0.0
requests>=2.31.0
pydantic>=2.0.0
python-dotenv>=1.0.0
platformdirs>=4.0.0
```

#### 1.3 Configuration Management
- Create `~/.config/threatconnect-cli/config.toml` using `platformdirs`
- Support environment variables as fallback
- Implement secure credential storage
- Add configuration for:
  - API credentials (access ID, secret key)
  - Instance name
  - Default owner
  - UI preferences (theme, keybindings)
  - Results per page (pagination)

#### 1.4 API Client Foundation
Refactor existing API code into modular client:
- Base `ThreatConnectClient` class with HMAC authentication
- Proper error handling with custom exceptions
- Response validation using Pydantic models
- Logging integration
- Rate limiting support

#### 1.5 Data Models
Define Pydantic models for:
- `Indicator` with all fields from API
- `Group` with all fields from API
- `Tag` for tag data
- `Attribute` for attribute data
- `Association` for relationships between objects
- `SearchResults` with pagination metadata

### Deliverables
- ✅ Working project structure
- ✅ Configuration system
- ✅ API client with authentication
- ✅ Data models with validation
- ✅ Unit tests for API client

---

## Phase 2: Basic TUI Implementation (Weeks 3-4)

### Objectives
- Create basic Textual application with layout
- Implement search functionality
- Display results in table format
- Add keyboard navigation

### Tasks

#### 2.1 Main Application Layout
Create main screen with three-panel layout:
```
┌─────────────────────────────────────────────────────┐
│ ThreatConnect CLI - [Instance Name]                 │
├─────────────────────────────────────────────────────┤
│ Search: [Indicators ▼] [________________________]   │
├─────────────────────────────────────────────────────┤
│ Results (23)                                        │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Type │ Summary        │ Rating │ Confidence    │ │
│ │ 🌐   │ 192.168.1.1   │ ⭐⭐⭐ │ 85%          │ │
│ │ 📧   │ evil@bad.com  │ ⭐⭐⭐⭐│ 95%          │ │
│ └─────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────┤
│ Page 1/3 │ ↑/↓: Navigate │ Enter: Details │ ?: Help│
└─────────────────────────────────────────────────────┘
```

#### 2.2 Search Input Widget
- Dropdown to select search type (Indicators / Groups / Both)
- Text input for query (supports indicator value or TQL)
- Auto-detect indicator type for simple searches
- TQL syntax highlighting (future enhancement)
- Search history with up/down arrows

#### 2.3 Results Table
Implement `DataTable` widget from Textual:
- Columns: Icon, Type, Summary, Date Added, Rating, Confidence, Owner
- Row selection with arrow keys
- Visual indicators (icons for types)
- Color coding based on rating/confidence
- Sorting by columns (click or keyboard shortcut)
- Row highlighting on selection

#### 2.4 Keyboard Navigation
Implement keybindings:
- `↑/↓` or `k/j` (vim): Navigate rows
- `←/→` or `h/l` (vim): Navigate pages
- `g/G`: Jump to top/bottom
- `1-9`: Jump to row number
- `Tab`: Cycle through panels
- `Enter`: View details
- `/`: Focus search
- `?`: Show help
- `q`: Quit
- `Ctrl+C`: Force quit

#### 2.5 Status Bar
- Current page / total pages
- Total results count
- Active keybindings hints
- Connection status indicator

### Deliverables
- ✅ Functional TUI with layout
- ✅ Search input and submission
- ✅ Results table with data
- ✅ Keyboard navigation
- ✅ Status bar with info

---

## Phase 3: Advanced Search & Filtering (Weeks 5-6)

### Objectives
- Implement TQL search support
- Add advanced filtering options
- Support owner specification
- Implement pagination with lazy loading

### Tasks

#### 3.1 TQL Integration
- Add TQL query builder UI
- Implement TQL validation
- Support both simple (summary) and TQL searches
- Query history and favorites
- TQL autocomplete suggestions (use OPTIONS endpoints)

Reference: [TQL Documentation](https://knowledge.threatconnect.com/docs/threatconnect-query-language-tql)

#### 3.2 Advanced Filters Panel
Add collapsible filter panel:
```
┌─ Filters ──────────────────┐
│ Type: [All Types      ▼]   │
│ Owner: [Default       ▼]   │
│ Rating: [⭐ 1+] [☐ Unrated]│
│ Confidence: [0%────100%]   │
│ Date Range:                │
│   From: [2024-01-01]       │
│   To:   [2025-11-22]       │
│ Tags: [________________]   │
│                            │
│ [Apply] [Reset] [Close]    │
└────────────────────────────┘
```

#### 3.3 Pagination Implementation
- Lazy loading with `resultStart` and `resultLimit` params
- Default 100 results per page (configurable)
- Background prefetching of next page
- Virtual scrolling for large datasets
- Page number input for direct navigation

Reference: [Pagination Docs](https://docs.threatconnect.com/en/latest/rest_api/overview.html#pagination)

#### 3.4 Owner Management
- Fetch available owners via API
- Dropdown selection in filters
- Remember last used owner
- Support for cross-organization searches

### Deliverables
- ✅ TQL query support
- ✅ Advanced filter panel
- ✅ Pagination with lazy loading
- ✅ Owner selection

---

## Phase 4: Detail View & Associations (Weeks 7-8)

### Objectives
- Implement detailed view for selected items
- Display tags and attributes
- Show associated Groups/Indicators
- Support navigation between associated items

### Tasks

#### 4.1 Detail View Panel
Create expandable detail view:
```
┌─ Indicator Details ──────────────────────────────────┐
│ 🌐 Address: 192.168.1.1                              │
│                                                       │
│ Basic Information:                                    │
│   Type:          Address (IPv4)                       │
│   Date Added:    January 15, 2024 14:32:10           │
│   Last Modified: November 22, 2025 09:15:43          │
│   Rating:        ⭐⭐⭐ (3.0/5.0)                      │
│   Confidence:    85%                                  │
│   Owner:         MyOrganization                       │
│   Active:        Yes                                  │
│                                                       │
│ Description:                                          │
│   Known C2 server for malware family XYZ...          │
│                                                       │
│ Tags (3):                                             │
│   🏷️ malware  🏷️ c2  🏷️ apt29                       │
│                                                       │
│ Attributes (2):                                       │
│   📎 Source: OSINT Report #1234                       │
│   📎 First Seen: 2024-01-10                           │
│                                                       │
│ Associated Groups (2):                                │
│   🚨 Incident: Network Intrusion Jan 2024            │
│   💀 Adversary: APT29                                │
│                                                       │
│ Associated Indicators (3):                            │
│   📄 File: a1b2c3d4... (SHA-256)                     │
│   🖥️ Host: malicious.example.com                     │
│   🔗 URL: http://192.168.1.1/payload                 │
│                                                       │
│ [Press 'a' to view associations] [Press 'e' to edit] │
└───────────────────────────────────────────────────────┘
```

#### 4.2 Tags & Attributes Retrieval
- Fetch tags with `?includeTags=true`
- Fetch attributes with `?includeAttributes=true`
- Display in organized sections
- Support filtering by tag
- Show attribute types and values

Reference: [Tags & Attributes Docs](https://docs.threatconnect.com/en/latest/rest_api/overview.html#retrieving-an-item-s-tags-and-attributes)

#### 4.3 Associations Display
- Show associated Groups when viewing Indicators
- Show associated Indicators when viewing Groups
- Support bidirectional navigation
- Highlight relationship types
- Allow expanding to view association details

#### 4.4 Navigation Enhancements
- Breadcrumb navigation for drilldown
- Back/forward history (`Alt+←` / `Alt+→`)
- Jump to associated item with `Enter`
- Open web link in browser (`Ctrl+O`)

### Deliverables
- ✅ Detail view panel
- ✅ Tags and attributes display
- ✅ Associations visualization
- ✅ Enhanced navigation

---

## Phase 5: Groups Support (Weeks 9-10)

### Objectives
- Full Groups API integration
- Group-specific search and display
- Combined Indicator + Group searches
- Group type-specific icons and formatting

### Tasks

#### 5.1 Groups API Client
Implement `GroupsAPI` class:
- Search groups with TQL
- Retrieve group details
- Fetch group associations
- Support all group types (Adversary, Campaign, Document, Email, Event, Incident, IntrusionSet, Report, Signature, Threat)

#### 5.2 Group Results Display
Extend results table for Groups:
- Group-specific columns: Type, Name, Date Added, Event Date (for Events), Owner
- Type-specific icons (💀 Adversary, 🎯 Campaign, etc.)
- Group status indicators
- Associated indicator count badge

#### 5.3 Group Detail View
Create group-specific detail layout:
- Group metadata (name, description, dates)
- Event-specific fields (event date, status)
- Document-specific fields (file name, file size)
- Associated Indicators section
- Associated Groups section
- Tags and Attributes

#### 5.4 Combined Search Mode
- Search both Indicators and Groups simultaneously
- Tabbed view to switch between result types
- Visual separation in results
- Unified keybindings

### Deliverables
- ✅ Groups API integration
- ✅ Group search and display
- ✅ Group detail view
- ✅ Combined search mode

---

## Phase 6: Polish & User Experience (Weeks 11-12)

### Objectives
- Add visual polish with Rich styling
- Implement theming support
- Add loading indicators and async operations
- Improve error handling and messaging
- Create comprehensive help system

### Tasks

#### 6.1 Visual Enhancements
- Custom CSS styling for modern look
- Nerd Fonts integration for powerline glyphs
- Color schemes (dark/light themes)
- Syntax highlighting for TQL
- Progress bars for searches
- Sparklines for trends (if applicable)

Reference: [Rich Library](https://rich.readthedocs.io/)

#### 6.2 Async Operations
- Background search execution
- Non-blocking API calls
- Loading spinners during requests
- Cancel operation support (`Ctrl+C` to cancel, not quit)
- Status notifications

#### 6.3 Error Handling
- User-friendly error messages
- API error code mapping
- Retry logic with exponential backoff
- Offline mode detection
- Validation feedback

#### 6.4 Help System
Comprehensive help screen:
- Keyboard shortcuts reference
- TQL syntax guide
- Quick start tutorial
- Configuration help
- API endpoint references

#### 6.5 Configuration UI
Add settings screen:
- Edit API credentials
- Change instance
- Customize keybindings
- Set theme preferences
- Configure pagination

### Deliverables
- ✅ Polished UI with theming
- ✅ Async operations
- ✅ Comprehensive error handling
- ✅ Help system
- ✅ Configuration UI

---

## Phase 7: Advanced Features (Weeks 13-14)

### Objectives
- Export functionality
- Bulk operations
- Search templates/bookmarks
- Performance optimizations
- Caching layer

### Tasks

#### 7.1 Export Functionality
- Export results to JSON
- Export results to CSV
- Export results to Markdown
- Copy selected items to clipboard
- Export with associations

#### 7.2 Bulk Operations
- Multi-select in results table (Space to toggle)
- Bulk tag operations
- Bulk export
- Batch API integration (future)

#### 7.3 Search Management
- Save search queries
- Search history
- Favorite searches
- Quick filters (recently viewed, high confidence, etc.)

#### 7.4 Performance Optimizations
- Results caching with TTL
- API response caching
- Virtual scrolling optimization
- Lazy loading of associations
- Background prefetching

#### 7.5 Advanced TQL Features
- TQL query builder wizard
- Field suggestions from OPTIONS endpoints
- Query validation before submission
- Query templates

### Deliverables
- ✅ Export functionality
- ✅ Bulk operations
- ✅ Search management
- ✅ Performance optimizations
- ✅ Advanced TQL features

---

## Phase 8: Testing & Documentation (Weeks 15-16)

### Objectives
- Comprehensive test coverage
- User documentation
- Developer documentation
- Performance testing
- Release preparation

### Tasks

#### 8.1 Testing
- Unit tests for all modules (pytest)
- Integration tests for API client
- UI tests for Textual widgets
- End-to-end workflow tests
- Error scenario testing
- Load testing with large datasets

#### 8.2 Documentation
- User guide with screenshots
- Installation instructions
- Configuration guide
- TQL quick reference
- Troubleshooting guide
- API reference for developers

#### 8.3 Performance Benchmarking
- Measure response times
- Optimize slow operations
- Memory profiling
- Startup time optimization

#### 8.4 Packaging
- Create `setup.py` and `pyproject.toml`
- PyPI package preparation
- Create release binaries (PyInstaller)
- Docker container (optional)

### Deliverables
- ✅ Test suite with >80% coverage
- ✅ Complete documentation
- ✅ Performance benchmarks
- ✅ Release package

---

## Technical Specifications

### UI Component Details

#### Color Scheme
Based on threat intelligence conventions:
- **Critical/High (Red)**: Rating 4-5, Confidence >90%
- **Medium (Yellow)**: Rating 2-3, Confidence 60-90%
- **Low (Green)**: Rating 0-1, Confidence <60%
- **Info (Blue)**: Metadata, timestamps
- **Accent (Cyan)**: Selected items, focus

#### Icon Mappings
See "Supported ThreatConnect Data Types" section above for complete icon reference.

#### Responsive Layout
- Minimum terminal size: 80x24
- Recommended: 120x40
- Support terminal resize events
- Collapsible panels for small screens

### API Integration Patterns

#### Authentication
```python
def generate_auth_header(api_path: str, query_string: str,
                         http_method: str, timestamp: str) -> str:
    message = f"{api_path}{query_string}:{http_method}:{timestamp}"
              if query_string else f"{api_path}:{http_method}:{timestamp}"
    signature = base64.b64encode(
        hmac.new(tc_secretkey.encode(), message.encode(),
                hashlib.sha256).digest()
    ).decode()
    return f"TC {tc_accessid}:{signature}"
```

#### TQL Query Construction
```python
# Simple summary search
tql = f'typeName in ("Address") and summary in ("192.168.1.1")'

# Advanced TQL
tql = f'(typeName in ("Address", "Host")) and (rating > 3) and (dateAdded > "2024-01-01")'

# Encode for URL
encoded_tql = urllib.parse.quote(tql)
url = f'/api/v3/indicators?tql={encoded_tql}'
```

#### Pagination Pattern
```python
# First page
url = '/api/v3/indicators?resultStart=0&resultLimit=100'

# Subsequent pages
url = f'/api/v3/indicators?resultStart={page * limit}&resultLimit={limit}'
```

### State Management

Use Textual's reactive system:
```python
class ResultsView(Widget):
    results: Reactive[list] = Reactive([])
    selected_index: Reactive[int] = Reactive(0)

    def watch_selected_index(self, old: int, new: int) -> None:
        # React to selection changes
        self.load_details(self.results[new])
```

### Configuration File Format

`~/.config/threatconnect-cli/config.toml`:
```toml
[api]
access_id = "your-access-id"
secret_key = "your-secret-key"  # Consider keyring integration
instance = "yourcompany"

[ui]
theme = "dark"  # dark, light, monokai, etc.
results_per_page = 100
show_confidence = true
show_rating = true

[keybindings]
quit = "q"
search = "/"
help = "?"
# ... custom keybindings

[cache]
enabled = true
ttl_seconds = 300

[defaults]
owner = "MyOrganization"
search_type = "indicators"  # indicators, groups, both
```

## Dependencies & Compatibility

### Python Version
- Minimum: Python 3.9
- Recommended: Python 3.11+

### Core Dependencies
- `textual>=0.90.0` - TUI framework
- `rich>=13.0.0` - Text formatting and styling
- `requests>=2.31.0` - HTTP client
- `pydantic>=2.0.0` - Data validation
- `python-dotenv>=1.0.0` - Environment management
- `platformdirs>=4.0.0` - Cross-platform config paths

### Development Dependencies
- `pytest>=7.0.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-cov>=4.0.0` - Coverage reporting
- `black>=24.0.0` - Code formatting
- `mypy>=1.0.0` - Type checking
- `textual-dev>=1.0.0` - Textual development tools

### Terminal Requirements
- UTF-8 support
- 256 colors minimum (true color recommended)
- Nerd Fonts for optimal icon display

## Risk Assessment & Mitigation

### Risks

1. **API Rate Limiting**
   - Mitigation: Implement request caching, batch requests where possible, user-configurable delays

2. **Large Result Sets**
   - Mitigation: Pagination, virtual scrolling, lazy loading, result limit warnings

3. **Network Latency**
   - Mitigation: Async operations, loading indicators, timeout handling, offline mode

4. **Breaking API Changes**
   - Mitigation: API version pinning, graceful degradation, comprehensive error handling

5. **Learning Curve**
   - Mitigation: Interactive tutorial, comprehensive help, sensible defaults, keyboard shortcut hints

### Security Considerations

1. **Credential Storage**
   - Use system keyring for secret storage (future enhancement)
   - File permissions on config files (600)
   - Environment variable support

2. **HTTPS Only**
   - Enforce HTTPS for all API calls
   - Certificate validation

3. **Input Validation**
   - Sanitize all user inputs
   - TQL injection prevention
   - Pydantic model validation

## Success Metrics

### User Experience
- ✅ Application starts in <2 seconds
- ✅ Search results display in <1 second (cached) or <3 seconds (API)
- ✅ Keyboard navigation feels responsive (<100ms)
- ✅ All core features accessible via keyboard
- ✅ Help accessible within 2 keystrokes

### Code Quality
- ✅ >80% test coverage
- ✅ Type hints on all public APIs
- ✅ Zero critical linter warnings
- ✅ All documentation up to date

### Functionality
- ✅ Support all indicator types
- ✅ Support all group types
- ✅ TQL query validation
- ✅ Pagination working for >10,000 results
- ✅ Export in multiple formats

## Future Enhancements (Post-v1.0)

### Phase 9+: Advanced Features
- Real-time updates (WebSocket support if available)
- Graph visualization of associations (ASCII art or browser-based)
- Machine learning insights integration
- Collaborative features (shared searches, annotations)
- Integration with other threat intel platforms
- Playbook/automation support
- Custom indicator/group creation
- Bulk import from CSV/JSON
- API v4 support (when available)
- Plugin system for extensibility

## Conclusion

This modernization plan transforms the ThreatConnect CLI from a basic query tool into a professional-grade TUI application that provides comprehensive access to ThreatConnect's Indicators and Groups through an intuitive, keyboard-driven interface. The phased approach ensures incremental value delivery while maintaining code quality and user experience throughout development.

By leveraging modern TUI frameworks (Textual + Rich) and following established design patterns, the resulting application will be maintainable, extensible, and user-friendly. The focus on AI-assisted development through clear documentation and patterns will enable rapid iteration and community contributions.

---

**Document Version**: 1.0
**Last Updated**: 2025-11-22
**Status**: Approved for Implementation
