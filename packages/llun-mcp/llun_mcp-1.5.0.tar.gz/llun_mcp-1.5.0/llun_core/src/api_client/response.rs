use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct Response {
    pub detected_issues: Vec<DetectedIssue>,
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct DetectedIssue {
    pub rule_code: String,
    pub name: String,
    pub file_path: String,
    pub brief_description: String,
    pub explanation: String,
    pub suggested_alternative: String,
    pub code_snippet: String,
}
