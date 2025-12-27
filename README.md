# AI Time Estimator

AI Time Estimator is a lightweight Python CLI tool that estimates how long a task will take to complete.

The user provides a task description in the terminal, and the tool returns a structured JSON estimate including total time, a range, a step by step breakdown, assumptions, and risks.

This project is intentionally simple and self contained, designed to demonstrate how to build a reliable command line tool using the OpenAI Responses API with strict JSON output and validation.

---

## What This Project Does

- Prompts the user for a task description via the command line
- Sends the task to the OpenAI Responses API
- Generates a time estimate with:
  - Total estimated minutes
  - A realistic time range
  - A breakdown of steps with minutes per step
  - Assumptions made
  - Potential risks
- Validates the AI response to ensure correct structure and data types
- Always returns valid JSON, even when errors occur

This makes the tool suitable for automation, scripting, or integration into other workflows.

---

## Technologies Used

- Python 3
- OpenAI Python SDK (Responses API)
- python dotenv for environment variable management
- uv for virtual environment and dependency management

### Standard Python Libraries

- json
- os
- sys
- typing

---

## How It Works

### Environment Setup

- The OpenAI API key is stored in a `.env` file
- python dotenv loads the key into the environment at runtime

### User Input

- The CLI prompts the user to describe a task
- Input is validated to ensure it is not empty

### Prompt Construction

- A structured prompt is built with strict instructions
- The AI is instructed to return only valid JSON with a fixed schema

### API Call

- The OpenAI Responses API is called using the official SDK
- JSON mode is enabled to enforce structured output

### Parsing and Validation

- The response is parsed into a Python dictionary
- The output is validated to ensure:
  - Correct keys
  - Correct data types
  - Breakdown minutes sum to total minutes

### Output

- The final result is printed as formatted JSON
- If any step fails, a fallback JSON error response is returned

---

## Setup and Usage

1. Clone the repository
2. Create a virtual environment using uv
3. Install dependencies
4. Add your OpenAI API key to a `.env` file
5. Run the CLI

---

## Design Principles

- Single file implementation
- No external datasets or file writes
- Predictable and validated JSON output
- Defensive error handling
- Readable and maintainable code
