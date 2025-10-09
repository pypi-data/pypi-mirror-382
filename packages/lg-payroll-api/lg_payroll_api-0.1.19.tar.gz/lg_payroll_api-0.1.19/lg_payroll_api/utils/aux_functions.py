# This module contains auxiliary functions to transform data
import json
import re
from os import path
from typing import Union


def clean_none_values_dict(data: dict) -> dict:
    """Remove none fields from dictionary."""

    result: dict = {}
    for key, value in data.items():
        if value != None:
            if isinstance(value, dict):
                result[key] = clean_none_values_dict(value)
                if result[key] == {}:
                    result[key] = None

            elif isinstance(value, list):
                if len(value) > 0:
                    if isinstance(value[0], dict):
                        result[key] = [clean_none_values_dict(item) for item in value]
                        if result[key] == []:
                            result[key] = None

                    else:
                        result[key] = value

                else:
                    result[key] = value

            else:
                result[key] = value

    return result


def extract_file_extension(file_name: str) -> str:
    pattern = r"\.([a-zA-Z0-9]+)$"
    match = re.search(pattern, file_name)

    if match:
        return match.group(1)

    else:
        return None


def read_json_file(file_path: str) -> Union[dict, list[dict]]:
    if not path.exists(file_path):
        raise FileNotFoundError(f"File not found. {file_path}")

    with open(file_path, "r") as f:
        data = json.loads(f.read())

    return data


def bool_to_int(value: bool) -> int:
    if isinstance(value, bool):
        value = int(value)

    return value
