import os
from typing import Dict, List, Tuple, Type, Union

class AbstractDataFileFormat:
    extensions: Union[List[str], Tuple[str, ...]]
    name: str = ""

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        
        # Check if extensions are defined
        if not hasattr(cls, "extensions"):
            raise ValueError(f"{cls.__name__}.extensions class attribute must be defined")
        
        # Check if extensions are a list or tuple
        if not isinstance(cls.extensions, (list, tuple)):
            raise TypeError(f"{cls.__name__}.extensions must be a list or tuple")
        
        # Check if extensions are not empty
        if len(cls.extensions) == 0:
            raise ValueError(f"{cls.__name__} has no extension set: please add extensions in the DataFileFormat class")
        
        # Check if all extensions are strings
        if not all(isinstance(extension, str) for extension in cls.extensions):
            raise TypeError(f"{cls.__name__}.extensions must contain only strings")
        
        # Ensure that the extensions are unique
        cls.extensions = tuple(set(cls.extensions))
        
        # Check if the name is a string
        if not isinstance(cls.name, str):
            raise TypeError(f"{cls.__name__}.name must be a string")

    @classmethod
    def _dump(
        cls: Type["AbstractDataFileFormat"],
        filepath: str,
        dataDict: Dict[str, object],
    ) -> None:
        raise NotImplementedError(f"{cls.__name__}._dump method must be implemented")

    @classmethod
    def _load(cls: Type["AbstractDataFileFormat"], filepath: str) -> Dict[str, object]:
        raise NotImplementedError(f"{cls.__name__}._load method must be implemented")

    @classmethod
    def __isValidFilePath(cls: Type["AbstractDataFileFormat"], filepath: str) -> str:
        # Check if extension is not None
        if not hasattr(cls, "extensions"):
            raise ValueError(f"{cls}.extension class attribute must be defined")

        # Check if the filepath is a string
        if not isinstance(filepath, str):
            raise TypeError("filepath must be a string")

        # Check if the filepath is empty
        if filepath == "":
            raise ValueError("filepath must not be empty")
        
        # Get extension from file path
        fileExtension = os.path.splitext(filepath)[-1]

        # Check if extension is correct
        if not fileExtension in cls.extensions:
            raise ValueError(f"File extension must be {cls.extensions}")

        # Check if relative path is provided
        if not os.path.isabs(filepath):
            # Build the absolute path
            filepath = os.path.abspath(filepath)

        return filepath

    @classmethod
    def __isValidDataDict(cls: Type["AbstractDataFileFormat"], dataDict: Dict[str, object]) -> None:
        # Check if the dataDict is a dictionary
        if not isinstance(dataDict, dict):
            raise TypeError("dataDict must be a dictionary")

        # Check if the dataDict is empty
        if not dataDict:
            raise ValueError("dataDict must not be empty")

    @classmethod
    def dump(
        cls: Type["AbstractDataFileFormat"],
        filepath: str,
        dataDict: Dict[str, object],
    ) -> None:
        # Check if the path is valid
        filepath = cls.__isValidFilePath(filepath)

        # Check if the dataDict is valid
        cls.__isValidDataDict(dataDict)

        # Check if directory exists
        if not os.path.exists(dirname := os.path.dirname(filepath)):
            raise FileNotFoundError(f"Directory {dirname} does not exist")

        # Call the _dump method
        cls._dump(filepath, dataDict)

    @classmethod
    def getExtension(cls: Type["AbstractDataFileFormat"], extensionIndex: int = 0) -> str:
        if extensionIndex < 0 or extensionIndex >= len(cls.extensions):
            raise ValueError(f"Wrong extension index value: {extensionIndex} not in range [{0};{len(cls.extensions)}[")

        return cls.extensions[extensionIndex]

    @classmethod
    def load(cls: Type["AbstractDataFileFormat"], filepath: str) -> Dict[str, object]:
        # Check if the path is valid
        filepath = cls.__isValidFilePath(filepath)

        # Check if the file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File {filepath} does not exist")

        # Call the _load method
        return cls._load(filepath)
