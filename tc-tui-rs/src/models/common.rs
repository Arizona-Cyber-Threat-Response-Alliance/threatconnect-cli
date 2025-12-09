use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Tag {
    pub name: String,
    pub description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Attribute {
    pub id: i64,
    #[serde(rename = "type")]
    pub type_: String,
    pub value: String,
    #[serde(rename = "dateAdded")]
    pub date_added: DateTime<Utc>,
    #[serde(rename = "lastModified")]
    pub last_modified: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Association {
    pub id: i64,
    #[serde(rename = "type")]
    pub type_: String,
    #[serde(rename = "objectType")]
    pub object_type: String,
    pub summary: Option<String>,
    pub name: Option<String>,
}
