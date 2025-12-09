# OpenSpec: Data Aggregation & Statistics

## Purpose
This spec defines the logic for processing raw indicator results from the API into a structured format suitable for the TUI. It addresses the requirements for "High Level Stats" and grouping multiple records of the same indicator (e.g., across different owners).

## Requirements

### 1. Grouping Logic
Raw indicators returned by the API may contain duplicates if the same indicator (e.g., "1.2.3.4") exists in multiple Owners/Organizations.
- **Input**: `Vec<Indicator>` (Flat list of results)
- **Output**: `Vec<GroupedIndicator>`
- **Logic**:
  - Group by `summary` (case-insensitive).
  - A `GroupedIndicator` contains a list of the original `Indicator` records.
  - The TUI will iterate over `GroupedIndicator` objects for the main carousel navigation.
  - The `indicator_type` is derived from the first indicator in the group.

### 2. High-Level Statistics
Calculate aggregate statistics for the *entire* search result set.
- **Fields to Calculate**:
  - **Count**: Total number of unique indicators found.
  - **Earliest Time**: The oldest `dateAdded` across all records.
  - **Latest Last Modified**: The most recent `lastModified` across all records.
  - **Average Rating**: Mean of `rating` (0.0 - 5.0). 0.0 values are considered "unrated" and excluded from the average.
  - **Average Confidence**: Mean of `confidence` (0-100).
  - **Total Owners**: Count of unique `ownerName`s in the result set.
  - **Active Count**: Number of indicators marked as `active: true`.
  - **False Positives**: Count of indicators marked as False Positive.
    - Logic: Check `falsePositiveFlag == true` (API field) OR tag name equals "False Positive" (case-insensitive fallback).

### 3. Error Handling
- Handle cases where fields are null or missing (e.g., use `Option` types).
- "Earliest Time" and "Average Rating" should handle empty result sets gracefully (e.g., return `N/A` or `None`).

## Data Structures

```rust
pub struct GroupedIndicator {
    pub summary: String,
    pub indicator_type: String,
    pub indicators: Vec<Indicator>, // All records for this summary
}

pub struct SearchStats {
    pub total_count: usize,
    pub earliest_created: Option<DateTime<Utc>>,
    pub latest_modified: Option<DateTime<Utc>>,
    pub avg_rating: Option<f32>,
    pub avg_confidence: Option<f32>,
    pub unique_owners: usize,
    pub active_count: usize,
    pub false_positives: usize,
}
```

## Verification Steps
- Unit test the grouping logic with a mocked list of indicators containing duplicates. (Verified)
- Unit test the statistics calculation with edge cases (empty list, null ratings). (Verified)
