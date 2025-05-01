from typing import Any, Dict, Union

from .models import Folder, Note, Script


def parse_folder_contents(item: Dict[str, Any]) -> Union[Folder, Script, Note]:
    if item["type"] == "script":
        return Script(**item)
    elif item["type"] == "note":
        return Note(**item)
    elif item["type"] == "folder":
        # first coerce the contents list into correct types
        if "contents" in item:
            item["contents"] = [parse_folder_contents(nested_item) for nested_item in item["contents"]]
        else:
            item["contents"] = []
        return Folder(**item)
    raise ValueError(f"Unexpected type: {item['type']}")
