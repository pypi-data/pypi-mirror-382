use crate::api_client::Response;
use crate::formatters::{OutputFormatter, OutputFormatterError};

pub struct AzureFormatter;

/// make use of the output formatter abstraction
impl OutputFormatter for AzureFormatter {
    fn format(&self, response: &Response) -> Result<String, OutputFormatterError> {
        if response.detected_issues.is_empty() {
            return Ok("##[section]No architecture issues detected".to_string());
        }

        let mut output = String::new();

        for issue in &response.detected_issues {
            // Azure DevOps warning format
            output.push_str(&format!(
                "\n\n##vso[task.logissue type=warning]{}: Rule {} ({})\n{}\n{}",
                issue.file_path,
                issue.rule_code,
                issue.brief_description,
                issue.code_snippet,
                issue.explanation,
            ));
        }

        // Summary section
        output.push_str(&format!(
            "\n\n##vso[task.logissue type=info]Architecture Analysis Complete - {} issue(s) found\n",
            response.detected_issues.len()
        ));

        Ok(output)
    }
}
