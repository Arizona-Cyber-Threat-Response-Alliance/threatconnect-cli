# OpenSpec: Visual Polish & Details

## Purpose
This spec defines the styling, conditional rendering, and "quality of life" features to make the TUI beautiful and intuitive.

## Feature Requirements

### 1. Conditional Rendering
- **Description Field**:
    - If `description` is `None` or an empty string, **do not render** the "Description:" label or blank space.
    - If `description` is present, render it.
- **Empty Fields**: Generally hide fields that are N/A to reduce clutter, unless critical (like Rating, where 0 might be significant).

### 2. "Press Enter for All" (Lazy Loading)
- **Concept**: The initial search returns a lightweight summary (if supported by API optimization) or standard fields.
- **Action**: When focusing a card, pressing `Enter` (or a specific key like `d` for Details) fetches *full* details (Attributes, Tags, Associations) if they weren't already loaded.
- **UI Feedback**: Show a spinner or "Loading..." state during fetch.

### 3. Styling & Theming
- **Colors**:
    - **Summary**: Bold, High Contrast (e.g., White/Cyan).
    - **Rating**: Visual skulls (`💀`) or bars. Color code (Red for high, Green for low).
    - **Labels**: Muted color (e.g., Dark Gray/Blue).
    - **Values**: Bright/Standard color.
- **Borders**: Use Rounded borders (`Borders::ALL`) for the main card.
- **Owners**: If multiple owners exist, use distinct background colors or separator lines to distinguish them visually.

### 4. Rich Text
- Parse simple Markdown in descriptions if possible (optional), or at least handle indentation and newlines gracefully.

## Verification
- Visual inspection: Verify empty descriptions leave no gaps.
- Visual inspection: Verify colors are consistent and readable on dark backgrounds.
