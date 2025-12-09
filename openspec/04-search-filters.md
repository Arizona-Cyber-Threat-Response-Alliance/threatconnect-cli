# OpenSpec: Search & Filters

## Purpose
This spec defines the search functionality and the addition of sorting/filtering controls.

## Search Functionality
- **Input**: Text field at the top.
- **Logic**:
    - Default: `summary contains "INPUT"`.
    - Advanced: Support direct TQL input if the user prefixes with `tql:` (future proofing).
- **History**: Keep a small history of recent searches (optional but nice).

## Sorting & Filtering (Top Bar)
- **UI Location**: Just below the Search Input or integrated into the Header Stats area.
- **Interaction**:
    - **Sort**: Key `s` to cycle sort order.
        - Options: `Date Added (Newest)`, `Rating (Highest)`, `Confidence (Highest)`.
        - Visual: Show an arrow or label indicating current sort (e.g., "Sort: Date ↓").
    - **Filter**: Key `f` to cycle or open filter menu.
        - Options: `Type` (Address, Host, Email), `Active Only`.

## Implementation Details
- Since we are fetching up to 100 results (default), sorting can be done *client-side* in Rust on the `Vec<GroupedIndicator>` for instant feedback.
- Filtering can also be client-side to hide items from the carousel without re-querying the API immediately.

## Verification
- Test: Search for generic term, apply "Rating" sort, verify high ratings appear first.
- Test: Apply "Active Only" filter, verify inactive items disappear.
