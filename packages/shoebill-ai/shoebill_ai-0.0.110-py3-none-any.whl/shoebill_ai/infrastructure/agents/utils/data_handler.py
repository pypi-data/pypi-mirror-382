import json
import re
import logging

# Set up a logger for demonstration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_json_data(json_string: str) -> dict:
    """
    Parses a string to extract and load JSON data, with extensive cleaning and repair.

    This function attempts to handle various common malformations:
    - Extracts JSON from Markdown code blocks.
    - Strips leading/trailing non-JSON content and comments.
    - On failure, attempts a series of advanced repairs before a final parsing attempt.
    """
    if not json_string or not json_string.strip():
        logger.warning("Empty JSON string provided.")
        return {}

    # 1. First, strip any comments from the string
    json_string = re.sub(r'/\*.*?\*/', '', json_string, flags=re.DOTALL)
    json_string = re.sub(r'//.*', '', json_string)

    # 2. Extract content from Markdown blocks
    match = re.search(r'```(?:json)?\s*({.*?})\s*```', json_string, re.DOTALL)
    if match:
        json_string = match.group(1).strip()
    else:
        # 3. If no markdown, greedily find the main JSON object
        start = json_string.find('{')
        end = json_string.rfind('}')
        if start != -1 and end > start:
            json_string = json_string[start:end + 1]
        else:
            logger.warning("Could not find a valid JSON object structure '{...}' in the string.")
            return {}

    # 4. First attempt to parse the cleaned string
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        logger.warning(f"Primary JSON parse failed: {e}. Attempting advanced repair...")

        # 5. If it fails, run the advanced repair function and try again
        repaired_string = _repair_json_string(json_string)
        try:
            data = json.loads(repaired_string)
            logger.info("JSON parsed successfully after advanced repair.")
            return data
        except json.JSONDecodeError as e2:
            logger.error(f"Failed to parse JSON even after advanced repair: {e2}")
            logger.debug(f"Repaired string that failed parsing: {repaired_string}")
            return {}


def _repair_json_string(s: str) -> str:
    """
    Applies a series of advanced fixes to a string to make it valid JSON.
    Handles unquoted keys, single quotes, bad escapes, trailing commas, and unescaped control characters.
    """
    # Fixes that can be safely done with regex first
    s = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', s)  # Add quotes to unquoted keys
    s = re.sub(r'\bNone\b', 'null', s)
    s = re.sub(r'\bTrue\b', 'true', s)
    s = re.sub(r'\bFalse\b', 'false', s)
    s = re.sub(r',\s*([}\]])', r'\1', s)  # Fix trailing commas

    # Use a state machine to fix complex issues like quotes and escapes
    result = []
    in_string = False
    quote_char = ''
    i = 0
    while i < len(s):
        char = s[i]

        if not in_string:
            # Entering a string
            if char in "'\"":
                in_string = True
                quote_char = char
                result.append('"')  # Always normalize to double quotes
            else:
                result.append(char)
            i += 1
            continue

        # --- We are inside a string ---
        # Exiting a string
        if char == quote_char:
            in_string = False
            result.append('"')
            i += 1
        # Handling escaped characters
        elif char == '\\':
            if i + 1 < len(s):
                next_char = s[i + 1]
                # If it's an already valid escape sequence, keep it
                if next_char in '"\\/bfnrtu':
                    result.append('\\' + next_char)
                # If it's an escaped version of the current quote char, keep it
                elif next_char == quote_char:
                    result.append('\\"')
                # Otherwise, it's an invalid escape; escape the backslash itself
                else:
                    result.append('\\\\' + next_char)
                i += 2
            else:  # Dangling backslash at the end of the string
                result.append('\\\\')
                i += 1

        # *** NEW: Explicitly handle unescaped control characters ***
        elif char == '\n':
            result.append('\\n')
            i += 1
        elif char == '\r':
            result.append('\\r')
            i += 1
        elif char == '\t':
            result.append('\\t')
            i += 1
        # Add other control characters if needed, e.g., \b, \f

        # Regular character inside a string
        else:
            # Escape double quotes that were not escaped
            if char == '"':
                result.append('\\"')
            else:
                result.append(char)
            i += 1

    return "".join(result)