import json
from typing import Union


def parse_json(json_str: str) -> Union[dict, None]:
    """
    Safely parse a JSON string and replace single quotes with double quotes if necessary

    Args:
        json_str (str): JSON string

    Returns:
        dict: Dictionary with the JSON data or None if the JSON is not valid
    """
    try:
        # Correct the JSON format by replacing single quotes with double quotes
        corrected_json_str = json_str.replace("'", '"')
        return json.loads(corrected_json_str)
    except json.JSONDecodeError:
        return None
