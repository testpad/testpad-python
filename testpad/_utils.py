from typing import Any, Dict, Union

from .models import Folder, Note, Script


def parse_folder_contents(data: Dict[str, Any]) -> Union[Folder, Script, Note]:
    if data["type"] == "script":
        return Script(**data)
    elif data["type"] == "note":
        return Note(**data)
    elif data["type"] == "folder":
        # first coerce the contents list into correct types
        data["contents"] = [parse_folder_contents(cont) for cont in data["contents"]]
        return Folder(**data)
    raise ValueError(f"Unexpected type: {data['type']}")
