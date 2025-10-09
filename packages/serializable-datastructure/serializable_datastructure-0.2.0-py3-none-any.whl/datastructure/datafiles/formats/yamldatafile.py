import yaml
from typing import Dict, Type

from .abstractdatafileformat import AbstractDataFileFormat

class YamlDataFile(AbstractDataFileFormat):
    extensions = (".yml", ".yaml")
    name = "YAML"

    @classmethod
    def _dump(cls: Type["AbstractDataFileFormat"], filepath: str, dataDict: Dict[str, object]) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(
                dataDict,
                f,
                Dumper=yaml.CSafeDumper,
                allow_unicode=True,
                indent=4,
                default_flow_style=False,
                encoding="utf-8",
            )

    @classmethod
    def _load(cls: Type["AbstractDataFileFormat"], filepath: str) -> Dict[str, object]:

        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.load(f, Loader=yaml.CLoader)

    @classmethod
    def getExtension(cls: Type["AbstractDataFileFormat"], extensionIndex: int = 1) -> str:
        return AbstractDataFileFormat.getExtension(extensionIndex)