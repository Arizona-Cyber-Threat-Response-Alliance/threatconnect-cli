use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use super::common::{Tag, Attribute, Association, ListResponse};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Indicator {
    pub id: i64,
    #[serde(rename = "type")]
    pub type_: String,
    pub summary: String,
    #[serde(default)]
    pub rating: f32,
    #[serde(default)]
    pub confidence: i32,
    #[serde(rename = "dateAdded")]
    pub date_added: DateTime<Utc>,
    #[serde(rename = "lastModified")]
    pub last_modified: DateTime<Utc>,
    #[serde(rename = "ownerName")]
    pub owner_name: String,
    #[serde(rename = "ownerId")]
    pub owner_id: i64,
    #[serde(rename = "webLink")]
    pub web_link: String,

    pub description: Option<String>,
    #[serde(default = "default_active")]
    pub active: bool,
    pub source: Option<String>,

    #[serde(rename = "falsePositiveFlag", default)]
    pub false_positive_flag: bool,
    #[serde(rename = "falsePositives", default)]
    pub false_positives: i32,
    #[serde(default)]
    pub observations: i32,

    #[serde(default)]
    pub tags: ListResponse<Tag>,
    #[serde(default)]
    pub attributes: ListResponse<Attribute>,

    // Using rename to map from associatedGroups/associatedIndicators
    #[serde(rename = "associatedGroups", default)]
    pub associated_groups: ListResponse<Association>,
    #[serde(rename = "associatedIndicators", default)]
    pub associated_indicators: ListResponse<Association>,
}

fn default_active() -> bool {
    true
}
