use serde::{Deserialize, Serialize};
use super::indicator::Indicator;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResponse {
    pub data: Vec<Indicator>,
    pub status: String,
}
