# main.py
import json
import os
import sys
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv
from openai import OpenAI


REQUIRED_KEYS = {"total_minutes", "range_minutes", "breakdown", "assumptions", "risks"}


def print_json(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def error_payload(message: str) -> Dict[str, Any]:
    # Always return the required JSON shape, even on errors.
    return {
        "total_minutes": 0,
        "range_minutes": "0 to 0",
        "breakdown": [{"step": "Unable to estimate", "minutes": 0}],
        "assumptions": ["JSON output required.", "Estimation failed due to an error."],
        "risks": [message],
    }


def get_api_key() -> str:
    load_dotenv()  # loads OPENAI_API_KEY from .env into environment
    return (os.getenv("OPENAI_API_KEY") or "").strip()


def get_task_description() -> str:
    desc = input("Describe the task you want to estimate: ").strip()
    return desc


def build_instructions(task_description: str) -> str:
    # Important: the word "JSON" must appear in the context when using JSON mode.
    return f"""
You are an AI time estimation assistant.
Return ONLY valid JSON (no markdown, no extra text). JSON must match this exact shape:

{{
  "total_minutes": <integer>,
  "range_minutes": "<min> to <max>",
  "breakdown": [{{"step": "<string>", "minutes": <integer>}}],
  "assumptions": ["<string>", "..."],
  "risks": ["<string>", "..."]
}}

Rules:
- Minutes must be realistic for a single person.
- breakdown minutes should sum to total_minutes.
- range_minutes must be a string formatted exactly like "30 to 45".
- Include 3 to 7 breakdown steps.
- Include at least 2 assumptions and 2 risks.
- Do not include any keys besides the 5 required keys.
- If the task description is too vague, make reasonable assumptions and list them.

Task description:
{task_description}
""".strip()


def call_time_estimator(client: OpenAI, task_description: str) -> str:
    # Use the Responses API with JSON mode via text.format.
    response = client.responses.create(
        model="gpt-4o-mini",
        input=build_instructions(task_description),
        text={"format": {"type": "json_object"}},
    )
    return response.output_text


def validate_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    if set(payload.keys()) != REQUIRED_KEYS:
        raise ValueError(f"JSON must contain exactly these keys: {sorted(REQUIRED_KEYS)}")

    total = payload["total_minutes"]
    if not isinstance(total, int) or total < 0:
        raise ValueError("total_minutes must be a non-negative integer")

    rng = payload["range_minutes"]
    if not isinstance(rng, str) or " to " not in rng:
        raise ValueError('range_minutes must be a string like "30 to 45"')

    breakdown = payload["breakdown"]
    if not isinstance(breakdown, list) or not breakdown:
        raise ValueError("breakdown must be a non-empty array")

    for i, item in enumerate(breakdown):
        if not isinstance(item, dict):
            raise ValueError(f"breakdown[{i}] must be an object")
        if set(item.keys()) != {"step", "minutes"}:
            raise ValueError('Each breakdown item must have exactly keys: "step", "minutes"')
        if not isinstance(item["step"], str) or not item["step"].strip():
            raise ValueError('Each breakdown "step" must be a non-empty string')
        if not isinstance(item["minutes"], int) or item["minutes"] < 0:
            raise ValueError('Each breakdown "minutes" must be a non-negative integer')

    assumptions = payload["assumptions"]
    if not isinstance(assumptions, list) or not all(isinstance(x, str) and x.strip() for x in assumptions):
        raise ValueError("assumptions must be an array of non-empty strings")

    risks = payload["risks"]
    if not isinstance(risks, list) or not all(isinstance(x, str) and x.strip() for x in risks):
        raise ValueError("risks must be an array of non-empty strings")

    if sum(item["minutes"] for item in breakdown) != total:
        raise ValueError("Sum of breakdown minutes must equal total_minutes")

    return payload


def parse_json(text: str) -> Dict[str, Any]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {e}") from e
    if not isinstance(payload, dict):
        raise ValueError("Top-level JSON value must be an object")
    return payload


def main() -> None:
    api_key = get_api_key()
    if not api_key:
        print_json(
            error_payload(
                "Missing OPENAI_API_KEY. Create a .env file and set OPENAI_API_KEY, or export it in your shell."
            )
        )
        sys.exit(1)

    task = get_task_description()
    if not task:
        print_json(error_payload("No task description provided. Please enter a brief description of the task."))
        sys.exit(1)

    try:
        client = OpenAI()
        raw = call_time_estimator(client, task)
        payload = validate_payload(parse_json(raw))
        print_json(payload)
    except Exception as e:
        print_json(error_payload(f"API call or processing failed: {e}"))
        sys.exit(1)


if __name__ == "__main__":
    main()