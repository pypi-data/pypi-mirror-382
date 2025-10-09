import os
from typing import Dict

from .formats import dataFileFormatsDictionary

class DataFileInterface:
    @staticmethod
    def dump(filepath: str, dataDict: Dict[str, object]) -> None:
        # Get the file extension
        _, ext = os.path.splitext(filepath)

        # Check if the file extension is supported
        if ext in dataFileFormatsDictionary:
            dataFileFormatsDictionary[ext].dump(filepath, dataDict)
        else:
            raise ValueError(f'Unsupported file format: "{ext}"')

    @staticmethod
    def load(filepath: str) -> Dict[str, object]:
        # Get the file extension
        _, ext = os.path.splitext(filepath)

        # Check if the file extension is supported
        if ext in dataFileFormatsDictionary:
            return dataFileFormatsDictionary[ext].load(filepath)
        else:
            raise ValueError(f'Unsupported file format: "{ext}"')
