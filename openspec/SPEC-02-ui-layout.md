# OpenSpec: UI Layout & Navigation

## Status
**Implemented** (Phase 2)

## Purpose
This spec defines the user interface layout and navigation model, shifting from a simple vertical list to a "Carousel" style master-detail view.

## Layout Overview

The terminal screen is divided into three main vertical chunks:

1.  **Header / Stats (Top)**
    - Height: Fixed (7 lines)
    - Content: Search Input (Always visible) + High-Level Stats (Count, Unique Owners, Avg Rating, Avg Confidence, Active Count, False Positives).

2.  **Main Content (Middle)**
    - Height: Flexible (Min 10)
    - Layout:
        - **Left Arrow Indicator**: Visual cue (e.g., `<` or `◄`) displayed in a left column.
        - **Card View (Center)**: The currently selected `GroupedIndicator`, displaying Summary, Type, and Group Size.
        - **Right Arrow Indicator**: Visual cue (e.g., `>` or `►`) displayed in a right column.

3.  **Footer (Bottom)**
    - Height: Fixed (3 lines)
    - Content: Status messages, Key hints (e.g., "←/→ Next/Prev | e: Search | q: Quit").

## Navigation Model

### Horizontal (Carousel)
- **Keys**: `Left` / `Right` arrows.
- **Action**: Cycles through the `Vec<GroupedIndicator>`.
- **Animation**: Immediate switch.
- **Looping**: Wraps around at ends.

### Vertical (Detail Scroll)
- **Keys**: `Up` / `Down` arrows.
- **Action**: Reserved for Phase 3 (Detail Scrolling). Currently no-op or default behavior.

### Search Interaction
- **Key**: `e` (Edit) to focus the Search Input at the top.
- **Key**: `Enter` to execute search.
- **Behavior**: When search completes, focus returns to the Carousel (first item selected).

## Visual Indicators
- **Pagination**: "Item X of Y" displayed in the title of the card.
- **Owner Tabs**: Detailed owner view is part of Phase 3.

## Verification
- Manual test: Ensure Left/Right keys change the Summary displayed.
- Manual test: Stats update correctly after search.
