# Implementation Order

This document outlines the sequential steps to implement the ThreatConnect TUI Modernization.

## Phase 1: Data Logic (Non-UI)
1.  **Refactor Models**: Ensure `Indicator` model supports all necessary fields.
2.  **Implement Aggregation**: Create `src/logic/aggregation.rs` (or similar).
    - Implement grouping logic (`GroupedIndicator`).
    - Implement stats calculation (`SearchStats`).
3.  **Unit Tests**: Write tests for grouping and stats to ensure correctness before UI integration.

## Phase 2: Core UI Refactor
4.  **Layout Skeleton**: Modify `tui.rs` to split the screen into the new Header/Carousel/Footer layout.
5.  **Carousel Widget**: Implement the logic to display *one* `GroupedIndicator` at a time.
    - Handle Left/Right key events to switch indices.
6.  **Stats Header**: Render the `SearchStats` in the top chunk.

## Phase 3: Detailed Views & Visuals
7.  **Indicator Detail Card**: Create a rich widget to render the `GroupedIndicator`.
    - Handle multiple owners (loop through inner indicators).
    - Implement conditional rendering (hide empty descriptions).
    - Apply styling (colors, skulls).
8.  **Vertical Scrolling**: Implement `Paragraph` scrolling or `List` scrolling *within* the card for long content.

## Phase 4: Search & Filters
9.  **Sorting Logic**: Implement `sort_by` methods on `Vec<GroupedIndicator>`.
10. **Filter Logic**: Implement filtering predicates.
11. **Controls**: Add `s` and `f` key bindings and visual status indicators for current sort/filter state.

## Phase 5: Polish & Final Review
12. **Lazy Loading**: (Optional) Implement "Press Enter" to fetch more details if not fully loaded.
13. **Final Testing**: End-to-end usage testing against the real API.
