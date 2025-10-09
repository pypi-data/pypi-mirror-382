import json
from typing import Dict, Type
from .abstractdatafileformat import AbstractDataFileFormat


class JsonDataFile(AbstractDataFileFormat):
    extensions = (".json", )
    name = "JSON"

    @classmethod
    def _dump(cls: Type["AbstractDataFileFormat"], filepath: str,
            dataDict: Dict[str, object]) -> None:
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(dataDict, f, indent=4, sort_keys=True, ensure_ascii=False)

    @classmethod
    def _load(cls: Type["AbstractDataFileFormat"], filepath: str) -> Dict[str, object]:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

