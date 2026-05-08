---
name: add-logging-before-after
description: '**WORKFLOW SKILL** — Add logging statements before and after code sections or functions in Python code. USE FOR: debugging execution flow, monitoring performance, tracking code paths in Python applications. DO NOT USE FOR: setting up logging configuration, production logging, or non-Python code.'
---

# Add Logging Before & After

## Overview
This skill helps add logging statements before and after specific code sections, functions, or operations in Python code to aid in debugging and monitoring. It uses Python's built-in `logging` module.

## Workflow Steps

1. **Identify Target Code**
   - Use semantic search or grep to find functions/methods where logging should be added
   - Determine the appropriate logging level (debug, info, warning, error)
   - Check if logging is already imported

2. **Ensure Logging Setup**
   - If not present, add `import logging` at the top
   - Configure basic logging if needed: `logging.basicConfig(level=logging.INFO)`

3. **Add Before Logging**
   - Insert `logging.info("Starting [function/section name]")` at the beginning
   - Include relevant context like parameters or timestamps

4. **Add After Logging**
   - Insert `logging.info("Completed [function/section name]")` at the end
   - Include completion status or execution results

5. **Validate**
   - Run the code to ensure logging works
   - Check syntax and imports
   - Verify logs appear in console or file

## Usage Examples
- Add logging to track Streamlit app processing steps
- Debug topic modeling pipeline execution
- Monitor sentiment analysis batch processing

## Quality Criteria
- Use consistent logging format
- Include function names and key parameters in log messages
- Avoid logging sensitive data
- Ensure logging doesn't impact performance critically