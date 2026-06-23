import json
import re
from typing import Optional


def extrair_json_objeto(texto: str) -> Optional[dict]:
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", texto)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None


def extrair_json_array(texto: str) -> Optional[list]:
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        match = re.search(r"\[[\s\S]*\]", texto)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None
