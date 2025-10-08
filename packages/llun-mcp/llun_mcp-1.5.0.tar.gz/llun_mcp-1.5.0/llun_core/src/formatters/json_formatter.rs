use crate::api_client::Response;
use crate::formatters::{OutputFormatter, OutputFormatterError};

pub struct JsonFormatter;

/// make use of the output formatter abstraction
impl OutputFormatter for JsonFormatter {
    fn format(&self, response: &Response) -> Result<String, OutputFormatterError> {
        Ok(serde_json::to_string_pretty(response)?)
    }
}
