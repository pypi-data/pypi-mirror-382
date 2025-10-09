import pandas as pd
from datetime import date, datetime
from enum import Enum
from inspect import isclass
from typing import Any, Dict, Generator, Tuple, Type, TypeVar

from .datafiles.interface import DataFileInterface

T = TypeVar("T", bound="DataStructure")

class DataStructure:

    # Class attributes
    readOnly: bool = False

    def __init__(self, **kwargs: object) -> None:
        super().__init__()
        
        # Init all attributes
        self.__attributes: Dict[str, object] = kwargs

    @property
    def attributes(self) -> Dict[str, Any]:
        return self.__attributes

    def __iter__(self) -> Generator[Tuple[str, object]]:
        # Get the attributes of the Box class
        for key, value in self.attributes.items():

            if isinstance(value, DataStructure):
                yield key, dict(value)
            elif isinstance(value, list):
                yield key, [
                    dict(item) if isinstance(item, DataStructure) else item
                        for item in value
                ]
            elif isinstance(value, dict):
                yield key, {
                    subkey: dict(subvalue)
                    if isinstance(subvalue, DataStructure)
                    else subvalue
                    for subkey, subvalue in value.items()
                }
            elif isinstance(value, set):
                yield key, {
                    item.__dict__ if isinstance(item, DataStructure) else item
                    for item in value
                }
            elif isinstance(value, tuple):
                yield key, tuple(
                    item.__dict__ if isinstance(item, DataStructure) else item
                    for item in value
                )
            elif isinstance(value, pd.DataFrame):
                yield key, value.to_dict()
            elif isclass(value):
                yield key, value.__name__
            elif isinstance(value, Enum):
                yield key, value.value
            elif isinstance(value, (date, datetime)):
                yield key, value.isoformat()
            else:
                yield key, value

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({dict(self)})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def copy(self) -> "DataStructure":
        return self.__class__(**dict(self))

    def dump(self, filepath: str) -> None:
        # Call the _dump method
        DataFileInterface.dump(filepath, dict(self))
    
    def setAttribute(self, key: str, value: Any) -> None:
        if self.__class__.readOnly:
            raise ValueError(f"Can't set {key} attribute: {self.__class__.__name__} is read-only")
        
        self.__attributes[key] = value

    def setField(self, fieldName: str, value: Any, expectedType: type) -> bool:
        if not isinstance(value, expectedType):
            raise TypeError(f"{fieldName} must be {expectedType.__name__}, not {type(value).__name__}")

        if self.__attributes[fieldName] == value:
            return False

        # Set attribute value
        self.setAttribute(fieldName, value)
        
        return True

    @classmethod
    def load(cls: Type[T], filepath: str) -> T:
        # Load the data from the file
        dataDict = DataFileInterface.load(filepath)

        # Create a new data structure object
        return cls(**dataDict)
