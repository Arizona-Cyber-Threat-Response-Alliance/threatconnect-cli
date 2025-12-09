#[cfg(test)]
mod tests {
    use super::super::aggregation::{group_indicators, calculate_stats};
    use crate::models::indicator::Indicator;
    use crate::models::common::Tag;
    use chrono::Utc;

    fn create_mock_indicator(
        summary: &str,
        owner: &str,
        rating: f32,
        confidence: i32,
        active: bool,
        false_positive: bool,
    ) -> Indicator {
        Indicator {
            id: 0,
            type_: "Host".to_string(),
            summary: summary.to_string(),
            rating,
            confidence,
            date_added: Utc::now(),
            last_modified: Utc::now(),
            owner_name: owner.to_string(),
            owner_id: 1,
            web_link: "http://localhost".to_string(),
            description: None,
            active,
            source: None,
            false_positive_flag: false_positive,
            false_positives: if false_positive { 1 } else { 0 },
            observations: 0,
            tags: vec![],
            attributes: vec![],
            associated_groups: vec![],
            associated_indicators: vec![],
        }
    }

    #[test]
    fn test_grouping_logic() {
        let mut indicators = vec![
            create_mock_indicator("bad.com", "Owner A", 0.0, 50, true, false),
            create_mock_indicator("bad.com", "Owner B", 3.0, 70, true, false),
            create_mock_indicator("EVIL.EXE", "Owner A", 5.0, 90, true, false),
        ];

        // Add one with mixed case to test case-insensitivity
        let mixed = create_mock_indicator("Bad.com", "Owner C", 0.0, 0, false, false);
        indicators.push(mixed);

        let groups = group_indicators(indicators);

        assert_eq!(groups.len(), 2, "Should have 2 groups: bad.com and evil.exe");

        let bad_group = groups.iter().find(|g| g.summary.eq_ignore_ascii_case("bad.com")).expect("bad.com group missing");
        assert_eq!(bad_group.indicators.len(), 3, "bad.com should have 3 indicators");

        let evil_group = groups.iter().find(|g| g.summary.eq_ignore_ascii_case("evil.exe")).expect("evil.exe group missing");
        assert_eq!(evil_group.indicators.len(), 1, "evil.exe should have 1 indicator");
    }

    #[test]
    fn test_stats_calculation() {
        let i1 = create_mock_indicator("A", "O1", 4.0, 80, true, false);
        let i2 = create_mock_indicator("B", "O1", 2.0, 60, false, true); // False positive
        let i3 = create_mock_indicator("C", "O2", 0.0, 40, true, false); // 0 rating should be ignored

        // Add a tag-based false positive
        let mut i4 = create_mock_indicator("D", "O2", 0.0, 50, true, false);
        i4.tags.push(Tag { name: "False Positive".to_string(), description: None });

        let indicators = vec![i1, i2, i3, i4];
        let stats = calculate_stats(&indicators);

        assert_eq!(stats.total_count, 4);
        assert_eq!(stats.unique_owners, 2);
        assert_eq!(stats.active_count, 3); // i2 is inactive (if false positive usually inactive? but here I set active=false explicitly)
        // Actually I set i2 active=false in create_mock_indicator arg.

        assert_eq!(stats.false_positives, 2, "Should count 1 flag and 1 tag based FP");

        // Avg Rating: (4.0 + 2.0) / 2 = 3.0. i3 and i4 have 0.0.
        assert_eq!(stats.avg_rating, Some(3.0));

        // Avg Confidence: (80 + 60 + 40 + 50) / 4 = 230 / 4 = 57.5
        assert_eq!(stats.avg_confidence, Some(57.5));
    }
}
