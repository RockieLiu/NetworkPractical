# serialization.py
from __future__ import annotations
import json
import pickle
from enum import IntEnum
from typing import Any, Dict, List, Union
import xml.etree.ElementTree as ET


class Format(IntEnum):
    PICKLE = 0
    JSON = 1
    XML = 2


JsonType = Union[Dict[str, Any], List[Any], str, int, float, bool, None]


def to_xml(obj: JsonType, root_tag: str = "root") -> bytes:
    """Serialize a JSON-like object to simple XML (UTF-8 bytes)."""
    root = ET.Element(root_tag)
    _json_to_xml(obj, root)
    return ET.tostring(root, encoding="utf-8")


def from_xml(data: bytes) -> JsonType:
    """Deserialize XML bytes (must be produced by to_xml) to a JSON-like object."""
    root = ET.fromstring(data)
    return _xml_to_json(root)


def _json_to_xml(obj: JsonType, parent: ET.Element) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            child = ET.SubElement(parent, str(k))
            _json_to_xml(v, child)
    elif isinstance(obj, list):
        for item in obj:
            child = ET.SubElement(parent, "item")
            _json_to_xml(item, child)
    else:
        parent.text = "" if obj is None else str(obj)


def _xml_to_json(elem: ET.Element) -> JsonType:
    children = list(elem)
    if not children:
        text = elem.text or ""
        # best-effort primitive conversion
        if text.lower() in ("true", "false"):
            return text.lower() == "true"
        for cast in (int, float):
            try:
                return cast(text)
            except ValueError:
                pass
        return text
    # map or list
    if all(child.tag == "item" for child in children):
        return [_xml_to_json(c) for c in children]
    return {c.tag: _xml_to_json(c) for c in children}


def serialize(obj: JsonType, fmt: Format) -> bytes:
    if fmt == Format.PICKLE:
        return pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
    if fmt == Format.JSON:
        return json.dumps(obj, ensure_ascii=False).encode("utf-8")
    if fmt == Format.XML:
        return to_xml(obj)
    raise ValueError(f"Unsupported format: {fmt}")


def deserialize(data: bytes, fmt: Format) -> JsonType:
    if fmt == Format.PICKLE:
        # ⚠ 不要对不可信来源使用 pickle.load / loads
        return pickle.loads(data)
    if fmt == Format.JSON:
        return json.loads(data.decode("utf-8"))
    if fmt == Format.XML:
        return from_xml(data)
    raise ValueError(f"Unsupported format: {fmt}")

