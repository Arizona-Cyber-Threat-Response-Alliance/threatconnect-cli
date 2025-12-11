use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListResponse<T> {
    #[serde(default)]
    pub data: Vec<T>,
}

impl<T> Default for ListResponse<T> {
    fn default() -> Self {
        Self { data: Vec::new() }
    }
}

impl<T> ListResponse<T> {
    pub fn is_empty(&self) -> bool {
        self.data.is_empty()
    }

    pub fn iter(&self) -> std::slice::Iter<'_, T> {
        self.data.iter()
    }
}

impl<T> IntoIterator for ListResponse<T> {
    type Item = T;
    type IntoIter = std::vec::IntoIter<T>;

    fn into_iter(self) -> Self::IntoIter {
        self.data.into_iter()
    }
}

impl<'a, T> IntoIterator for &'a ListResponse<T> {
    type Item = &'a T;
    type IntoIter = std::slice::Iter<'a, T>;

    fn into_iter(self) -> Self::IntoIter {
        self.data.iter()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Tag {
    pub name: String,
    pub description: Option<String>,
}

impl Default for Tag {
    fn default() -> Self {
        Tag {
            name: String::new(),
            description: None,
        }
    }
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

impl Default for Attribute {
    fn default() -> Self {
        Attribute {
            id: 0,
            type_: String::new(),
            value: String::new(),
            date_added: Utc::now(),
            last_modified: Utc::now(),
        }
    }
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

impl Default for Association {
    fn default() -> Self {
        Association {
            id: 0,
            type_: String::new(),
            object_type: String::new(),
            summary: None,
            name: None,
        }
    }
}
