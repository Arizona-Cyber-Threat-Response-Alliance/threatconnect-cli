use std::collections::HashMap;
use chrono::{DateTime, Utc};
use crate::models::indicator::Indicator;

#[derive(Debug, Clone)]
pub struct GroupedIndicator {
    pub summary: String,
    pub indicator_type: String,
    pub indicators: Vec<Indicator>,
}

#[derive(Debug, Clone, Default)]
pub struct SearchStats {
    pub total_count: usize,
    #[allow(dead_code)]
    pub earliest_created: Option<DateTime<Utc>>,
    #[allow(dead_code)]
    pub latest_modified: Option<DateTime<Utc>>,
    pub avg_rating: Option<f32>,
    pub avg_confidence: Option<f32>,
    pub unique_owners: usize,
    pub active_count: usize,
    pub false_positives: usize,
}

pub fn group_indicators(indicators: Vec<Indicator>) -> Vec<GroupedIndicator> {
    let mut groups: HashMap<String, Vec<Indicator>> = HashMap::new();

    for indicator in indicators {
        let key = indicator.summary.to_lowercase();
        groups.entry(key).or_default().push(indicator);
    }

    // Convert map to Vec<GroupedIndicator>
    // Note: We take the 'type' from the first indicator in the group.
    // In a valid dataset, indicators with the same summary should have the same type.
    let mut result: Vec<GroupedIndicator> = groups
        .into_iter()
        .map(|(_, indicators)| {
            // Recover the original casing for summary from the first indicator if possible
            // But the map key is lowercase. Let's use the summary from the first indicator.
            let first = &indicators[0];
            let summary = first.summary.clone();
            let indicator_type = first.type_.clone();

            GroupedIndicator {
                summary,
                indicator_type,
                indicators,
            }
        })
        .collect();

    // Sort for deterministic output? Maybe by summary?
    result.sort_by(|a, b| a.summary.to_lowercase().cmp(&b.summary.to_lowercase()));
    result
}

pub fn calculate_stats(indicators: &[Indicator]) -> SearchStats {
    if indicators.is_empty() {
        return SearchStats::default();
    }

    let total_count = indicators.len();

    let earliest_created = indicators.iter().map(|i| i.date_added).min();
    let latest_modified = indicators.iter().map(|i| i.last_modified).max();

    let unique_owners = indicators
        .iter()
        .map(|i| i.owner_name.clone())
        .collect::<std::collections::HashSet<_>>()
        .len();

    let active_count = indicators.iter().filter(|i| i.active).count();

    // False Positives: Check flag OR tag
    let false_positives = indicators.iter().filter(|i| {
        if i.false_positive_flag {
            return true;
        }
        // Fallback: Check for tag named "False Positive" (case insensitive check might be safer)
        i.tags.iter().any(|t| t.name.eq_ignore_ascii_case("False Positive"))
    }).count();

    // Avg Rating: Ignore 0.0
    let (rating_sum, rating_count) = indicators.iter()
        .filter(|i| i.rating > 0.0)
        .fold((0.0f32, 0), |(sum, count), i| (sum + i.rating, count + 1));

    let avg_rating = if rating_count > 0 {
        Some(rating_sum / rating_count as f32)
    } else {
        None
    };

    // Avg Confidence
    let (conf_sum, conf_count) = indicators.iter()
        .fold((0, 0), |(sum, count), i| (sum + i.confidence, count + 1));

    let avg_confidence = if conf_count > 0 {
        Some(conf_sum as f32 / conf_count as f32)
    } else {
        None
    };

    SearchStats {
        total_count,
        earliest_created,
        latest_modified,
        avg_rating,
        avg_confidence,
        unique_owners,
        active_count,
        false_positives,
    }
}
