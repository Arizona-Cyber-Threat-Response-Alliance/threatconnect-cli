# OpenSpec: UI Layout & Navigation

## Purpose
This spec defines the user interface layout and navigation model, shifting from a simple vertical list to a "Carousel" style master-detail view.

## Layout Overview

The terminal screen is divided into three main vertical chunks:

1.  **Header / Stats (Top)**
    - Height: Fixed (approx 5-7 lines)
    - Content: Search Input (collapsed or active) + High-Level Stats (e.g., "Avg Rating: 3.5 | Owners: 5").

2.  **Main Content (Middle)**
    - Height: Flexible (Min 10)
    - Layout:
        - **Left Arrow Indicator**: Visual cue (e.g., `<` or `◄`) if previous items exist.
        - **Card View (Center)**: The currently selected `GroupedIndicator`.
        - **Right Arrow Indicator**: Visual cue (e.g., `>` or `►`) if next items exist.

3.  **Footer (Bottom)**
    - Height: Fixed (3 lines)
    - Content: Status messages, Key hints (e.g., "←/→ Next/Prev | ↑/↓ Scroll Detail | Enter: Search").

## Navigation Model

### Horizontal (Carousel)
- **Keys**: `Left` / `Right` arrows.
- **Action**: Cycles through the `Vec<GroupedIndicator>`.
- **Animation**: Immediate switch (no complex sliding animation required for MVP).
- **Looping**: Optional (user prefers stopping at ends, but looping is acceptable).

### Vertical (Detail Scroll)
- **Keys**: `Up` / `Down` arrows.
- **Action**: Scrolls the content *within* the currently selected Indicator Card.
- **Context**:
    - If a Grouped Indicator has multiple Owners, these keys might scroll through the stacked list of owner records.
    - If the description is long, these keys scroll the text viewport.

### Search Interaction
- **Key**: `e` (Edit) or `/` to focus the Search Input at the top.
- **Key**: `Enter` to execute search.
- **Behavior**: When search completes, focus returns to the Carousel (first item selected).

## Visual Indicators
- **Pagination**: "Item X of Y" displayed in the corner of the card.
- **Owner Tabs**: If an indicator has multiple owners, display tabs or a clear visual separator between them within the card.

## Verification
- Manual test: Ensure Left/Right keys change the Summary displayed.
- Manual test: Ensure Up/Down keys scroll long content without changing the selected Summary.
