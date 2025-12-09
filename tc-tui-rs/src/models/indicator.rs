use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use super::common::{Tag, Attribute, Association};

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

    #[serde(default)]
    pub tags: Vec<Tag>,
    #[serde(default)]
    pub attributes: Vec<Attribute>,

    // Using rename to map from associatedGroups/associatedIndicators
    #[serde(rename = "associatedGroups", default)]
    pub associated_groups: Vec<Association>,
    #[serde(rename = "associatedIndicators", default)]
    pub associated_indicators: Vec<Association>,
}

fn default_active() -> bool {
    true
}
