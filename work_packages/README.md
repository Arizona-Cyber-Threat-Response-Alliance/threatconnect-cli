# Work Packages - Parallel Development Guide

## Overview

This directory contains modular work packages designed for parallel development by multiple AI agents or developers. Each package is self-contained with clear interfaces, minimal dependencies, and comprehensive specifications.

## Package Status Dashboard

| Package | Module | Priority | Time | Dependencies | Status | Branch |
|---------|--------|----------|------|--------------|--------|--------|
| [Package 1](PACKAGE_1_DATA_MODELS.md) | Data Models | 🔴 High | 4-6h | None | ⚪ Ready | `module/1-data-models` |
| [Package 2](PACKAGE_2_API_CLIENT.md) | API Client | 🔴 High | 6-8h | 1, 3 | ⚪ Ready | `module/2-api-client` |
| [Package 3](PACKAGE_3_CONFIGURATION.md) | Configuration | 🔴 High | 3-4h | None | ⚪ Ready | `module/3-config` |
| [Package 4](PACKAGE_4_UTILITIES.md) | Utilities | 🟡 Medium | 3-4h | 1 | ⚪ Ready | `module/4-utilities` |
| Package 5 | Search Engine | 🟡 Medium | 5-6h | 2, 1 | 📝 Planned | `module/5-search` |
| Package 6 | State Manager | 🟡 Medium | 4-5h | 1 | 📝 Planned | `module/6-state` |
| Package 7a | Widget: SearchInput | 🟡 Medium | 3-4h | 1, 4 | 📝 Planned | `module/7-widget-search` |
| Package 7b | Widget: ResultsTable | 🟡 Medium | 4-5h | 1, 4 | 📝 Planned | `module/7-widget-table` |
| Package 7c | Widget: DetailView | 🟡 Medium | 4-5h | 1, 4 | 📝 Planned | `module/7-widget-detail` |
| Package 7d | Widget: StatusBar | 🟢 Low | 2-3h | 1 | 📝 Planned | `module/7-widget-status` |
| Package 8 | Screens | 🟡 Medium | 5-6h | 7a-d | 📝 Planned | `module/8-screens` |
| Package 9 | Main App | 🔴 High | 4-5h | 8, 3 | 📝 Planned | `module/9-main-app` |

**Legend**:
- ⚪ Ready to Start
- 🟦 In Progress
- ✅ Complete
- 🚫 Blocked
- 📝 Planned (spec not written yet)

## Parallel Development Phases

### Phase 1: Foundation (Can Start Immediately)

These packages have **NO dependencies** and can be developed in parallel:

- **Package 1: Data Models** (4-6 hours)
  - Define all Pydantic models
  - No dependencies
  - Provides interfaces for all other modules

- **Package 3: Configuration** (3-4 hours)
  - Config loading/saving
  - No dependencies
  - Needed by API client and main app

#### Suggested Assignment:
- **Agent A**: Package 1 (Data Models)
- **Agent B**: Package 3 (Configuration)

**Estimated Completion**: 1 day (parallel)

---

### Phase 2: Core Services (After Phase 1)

These packages depend on Phase 1 outputs:

- **Package 2: API Client** (6-8 hours)
  - Depends on: Package 1 (models), Package 3 (config)
  - Can start once model interfaces are defined

- **Package 4: Utilities** (3-4 hours)
  - Depends on: Package 1 (models - soft dependency)
  - Can start with stubs

#### Suggested Assignment:
- **Agent A**: Package 2 (API Client)
- **Agent B**: Package 4 (Utilities)

**Estimated Completion**: 1-2 days (parallel)

---

### Phase 3: Business Logic (After Phase 2)

- **Package 5: Search Engine** (5-6 hours)
  - Depends on: Package 2 (API), Package 1 (models)
  - Query building and search orchestration

- **Package 6: State Manager** (4-5 hours)
  - Depends on: Package 1 (models)
  - Application state management

#### Suggested Assignment:
- **Agent A**: Package 5 (Search Engine)
- **Agent B**: Package 6 (State Manager)

**Estimated Completion**: 1 day (parallel)

---

### Phase 4: UI Widgets (After Phases 1-2)

All widget packages can be developed **in parallel**:

- **Package 7a: SearchInput Widget** (3-4 hours)
- **Package 7b: ResultsTable Widget** (4-5 hours)
- **Package 7c: DetailView Widget** (4-5 hours)
- **Package 7d: StatusBar Widget** (2-3 hours)

Each widget:
- Depends on Package 1 (models) for data types
- Depends on Package 4 (utilities) for formatting
- Uses mock data for development
- Has clear Message interface

#### Suggested Assignment:
- **Agent A**: Package 7a + 7d (SearchInput + StatusBar)
- **Agent B**: Package 7b (ResultsTable)
- **Agent C**: Package 7c (DetailView)

**Estimated Completion**: 1 day (parallel)

---

### Phase 5: Integration (After Phase 4)

- **Package 8: Screens** (5-6 hours)
  - Depends on: All widgets (7a-d)
  - Composes widgets into screens

- **Package 9: Main App** (4-5 hours)
  - Depends on: Package 8 (screens), Package 3 (config)
  - Final integration

#### Suggested Assignment:
- **Agent A**: Package 8 (Screens)
- Then **Agent A**: Package 9 (Main App)

**Estimated Completion**: 1-2 days (sequential)

---

## Total Timeline

| Phase | Duration | Agents | Mode |
|-------|----------|--------|------|
| Phase 1 | 1 day | 2 | Parallel |
| Phase 2 | 1-2 days | 2 | Parallel |
| Phase 3 | 1 day | 2 | Parallel |
| Phase 4 | 1 day | 3 | Parallel |
| Phase 5 | 1-2 days | 1 | Sequential |

**Total Development Time**: 5-7 days with optimal parallelization

## Overlap Prevention Strategy

### 1. Clear Module Boundaries

Each package owns specific files:
```
Package 1 → tc_tui/models/*.py
Package 2 → tc_tui/api/*.py
Package 3 → tc_tui/config/*.py
Package 4 → tc_tui/utils/*.py
```

**No file is modified by multiple packages.**

### 2. Interface Contracts

All modules communicate through well-defined interfaces:

```python
# Package 1 exports
from tc_tui.models import Indicator, Group, SearchResult

# Package 2 exports
from tc_tui.api import ThreatConnectClient, IndicatorsAPI

# Package 3 exports
from tc_tui.config import ConfigManager, AppConfig
```

### 3. Mock Data for Development

All UI packages use mock data during development:

```python
# tests/fixtures/mock_data.py
MOCK_INDICATOR = {...}
MOCK_SEARCH_RESULT = {...}
```

This allows UI development without a working API client.

### 4. Branch Strategy

Each package has its own branch:
- `module/1-data-models`
- `module/2-api-client`
- `module/3-config`
- etc.

Integration happens on dedicated branches:
- `integration/phase-1`
- `integration/phase-2`
- etc.

### 5. Testing in Isolation

Each module must have:
- Unit tests with >80% coverage
- Mock external dependencies
- Integration test stubs

Example:
```python
# Package 7b testing (ResultsTable)
from tests.fixtures.mock_data import MOCK_SEARCH_RESULT

def test_table_display():
    table = ResultsTable()
    table.update_results(MOCK_SEARCH_RESULT)
    assert table.row_count == len(MOCK_SEARCH_RESULT.data)
```

## Integration Points

### Critical Integration Checkpoints

#### Checkpoint 1: After Phase 1
- Verify all models can be imported
- Verify model validation works
- Verify JSON serialization/deserialization

#### Checkpoint 2: After Phase 2
- Verify API client can authenticate
- Verify API client returns proper models
- Verify config loads correctly

#### Checkpoint 3: After Phase 3
- Verify search engine builds correct queries
- Verify state manager handles updates
- Integration test: search → API → models

#### Checkpoint 4: After Phase 4
- Verify all widgets render with mock data
- Verify widgets emit correct messages
- Verify widgets respond to state changes

#### Checkpoint 5: After Phase 5
- End-to-end test: search → API → display
- Performance test with large datasets
- Full user workflow test

## Communication Protocol

### For Agents Working in Parallel

1. **Before Starting**: Read the full package specification
2. **During Development**: Follow the exact file structure
3. **Interface Changes**: Document any deviations from spec
4. **Testing**: Run all tests before marking complete
5. **Integration**: Provide integration notes for next phase

### Integration Notes Template

Each completed package should provide:

```markdown
## Package X Integration Notes

### Completed
- [x] All specified files created
- [x] All tests passing
- [x] Type hints on all public functions
- [x] Docstrings complete

### Public API
- Exported classes: [list]
- Exported functions: [list]
- Mock data location: tests/fixtures/

### Deviations from Spec
- [Any changes made]

### Dependencies for Next Phase
- [What other packages need to know]

### Known Issues
- [Any issues or limitations]
```

## Quick Start for New Agent

### To Start a Package:

1. **Read the package specification** (PACKAGE_X_*.md)
2. **Check dependencies** - ensure prerequisite packages are complete
3. **Create branch**: `git checkout -b module/X-name`
4. **Create file structure** as specified
5. **Run tests frequently**: `pytest tests/test_X/`
6. **Follow acceptance criteria** for completion

### Example Workflow:

```bash
# Start Package 1 (Data Models)
git checkout -b module/1-data-models

# Create structure
mkdir -p tc_tui/models tests/test_models

# Develop following spec
# ... create files ...

# Test
pytest tests/test_models/ -v --cov=tc_tui/models

# Commit
git add tc_tui/models/ tests/test_models/
git commit -m "Implement data models (Package 1)"

# Push
git push -u origin module/1-data-models

# Open PR for integration
```

## Mock Data Strategy

### Location
All mock data in `tests/fixtures/mock_data.py`

### Coverage
- Mock Indicator (all fields)
- Mock Group (all fields)
- Mock SearchResult (with pagination)
- Mock API responses
- Mock configuration

### Usage
```python
from tests.fixtures.mock_data import MOCK_INDICATOR, MOCK_SEARCH_RESULT

# Use in tests
def test_widget():
    widget.set_data(MOCK_INDICATOR)
    assert widget.title == MOCK_INDICATOR["summary"]
```

## Quality Gates

Each package must pass:

- [ ] All unit tests passing
- [ ] Code coverage >80%
- [ ] All type hints present
- [ ] All docstrings complete
- [ ] No linter errors
- [ ] Integration contract verified
- [ ] Mock data provided (if applicable)

## FAQ

### Q: Can I start Package 2 before Package 1 is complete?

**A:** Yes, if Package 1 has defined the model interfaces (class signatures). Use stub models or Pydantic models with minimal fields initially.

### Q: What if I need to change a model from Package 1?

**A:** Document the change and communicate with all dependent packages. Ideally, extend rather than modify existing models.

### Q: How do I test widgets without a real API?

**A:** Use mock data from `tests/fixtures/mock_data.py`. Widgets should not directly import API client.

### Q: Can multiple widgets be developed simultaneously?

**A:** Yes! All widgets in Package 7 are independent. Assign each to different agents.

### Q: What if tests fail during integration?

**A:** Identify which contract is broken. Usually it's a mismatch between expected and actual interface. Fix in the providing module.

## Next Steps

1. **Review ARCHITECTURE.md** for system overview
2. **Review MODERNIZATION_PLAN.md** for full project scope
3. **Choose a package** from Phase 1 to start
4. **Read the package spec** thoroughly
5. **Create branch and begin development**

---

## Package Specifications

Available package specs:
- [PACKAGE_1_DATA_MODELS.md](PACKAGE_1_DATA_MODELS.md) - Pydantic models for all data
- [PACKAGE_2_API_CLIENT.md](PACKAGE_2_API_CLIENT.md) - ThreatConnect API client
- [PACKAGE_3_CONFIGURATION.md](PACKAGE_3_CONFIGURATION.md) - Config management
- [PACKAGE_4_UTILITIES.md](PACKAGE_4_UTILITIES.md) - Icons, formatters, validators

Additional packages (5-9) will be created as Phase 1 completes.

---

**Questions?** Review ARCHITECTURE.md for detailed integration contracts.

**Ready to Start?** Pick a package and create your branch!
