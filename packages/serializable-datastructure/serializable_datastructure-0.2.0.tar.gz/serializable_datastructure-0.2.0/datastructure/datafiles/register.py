from typing import Type
from .formats import AbstractDataFileFormat, dataFileFormatsDictionary, availableExtensions, dataFileFormats

def registerDatafileFormat(datafileFormat: Type[AbstractDataFileFormat]) -> None:
    global dataFileFormatsDictionary, availableExtensions

    if not issubclass(datafileFormat, AbstractDataFileFormat):
        raise ValueError(f"Expected a sub class of AbstractDataFileFormat, got {type(datafileFormat)}")
    
    if datafileFormat in dataFileFormats:
        raise ValueError(f"DataFileFormat {datafileFormat} is already registered")
    
    for extension in datafileFormat.extensions:
        if extension in dataFileFormatsDictionary:
            raise ValueError(f"Extension {extension} is already registered in the dictionary")

        if extension in availableExtensions:
            raise ValueError(f"Extension {extension} is already registered in available extensions")
    
    # Add the datafile format to the list
    dataFileFormats.append(datafileFormat)

    for extension in datafileFormat.extensions:
    
        # Add the datafile format to the dictionary
        dataFileFormatsDictionary[extension] = datafileFormat

        # Add the extension to the list of available extensions
        availableExtensions.add(extension)
