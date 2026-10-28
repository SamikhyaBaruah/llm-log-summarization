import os
import sys
import requests


def read_log(filename):
    """Read the build/error log."""
    try:
        with open(filename, "r") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        sys.exit(1)


def create_prompt(log_text):
    """Create a prompt for Gemini."""
    return f"""
You are a CI/CD debugging assistant.

Analyze the following build/test failure log.

Give a simple and short answer containing:

1. Root Cause
2. Failing Tests
3. Error Details
4. Suggested Fix

Build Log:
----------------
{log_text}
----------------
"""


def summarize_log(log_text):
    api_key = os.getenv("LLM_API_KEY")

    if not api_key:
        print("Error: LLM_API_KEY is not set.")
        sys.exit(1)

    url = (
    "https://generativelanguage.googleapis.com/v1beta/"
   "models/gemini-3.5-flash-lite:generateContent"
)

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": create_prompt(log_text)
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=60
        )

        response.raise_for_status()

        result = response.json()

        summary = result["candidates"][0]["content"]["parts"][0]["text"]

        print("\n========== LLM BUILD LOG SUMMARY ==========\n")
        print(summary)
        print("\n===========================================\n")

    except requests.exceptions.RequestException as error:
        print("API request failed:", error)

    except (KeyError, IndexError):
        print("Could not read the LLM response.")
        print(response.text)


if __name__ == "__main__":
    log = read_log("build.log")
    summarize_log(log)