# Build the dataFileFormats list
import itertools
from typing import Dict, List, Set, Type

from .abstractdatafileformat import AbstractDataFileFormat
from .jsondatafile import JsonDataFile
from .yamldatafile import YamlDataFile

"""
Build list of available data file formats

If new DataFileFormat classes are added, they must be added to the dataFileFormats list
"""
# Build the dataFileFormats list
dataFileFormats: List[Type[AbstractDataFileFormat]] = [
    JsonDataFile,
    YamlDataFile,
]

"""
Build the available extensions list and the data file formats dictionary
"""
# Build the available extensions list
__availableExtensions: List[str] = list(itertools.chain.from_iterable([
    dataFileFormat.extensions for dataFileFormat in dataFileFormats
]))

"""
Check if all data file formats are valid
"""
# Check if the extensions are unique
if len(__availableExtensions) != len(set(__availableExtensions)):
    raise ValueError("Extensions must be unique")

# Check if the extensions are not empty
if not __availableExtensions:
    raise ValueError("Extensions must not be empty")

# Check if all extensions are strings
unvalidDataFileFormats: List[Type[AbstractDataFileFormat]] = [
    dataFileFormat
    for dataFileFormat in dataFileFormats
    if not all(isinstance(extension, str) for extension in dataFileFormat.extensions)
]
if unvalidDataFileFormats != []:
    # Build the string with the unvalid extensions
    unvalidExtensionsString: str = ", ".join(
        [dataFileFormat.__name__ for dataFileFormat in unvalidDataFileFormats],
    )

    #
    raise TypeError(
        f"Extension must be a string for the following AbstractDataFileFormat subclass: {unvalidExtensionsString}",
    )

# Build available extensions set
availableExtensions: Set[str] = set(__availableExtensions)

# Delete the available extensions list
del __availableExtensions

# Build the data file formats dictionary
dataFileFormatsDictionary: Dict[str, Type[AbstractDataFileFormat]] = {
    extension: dataFileFormat \
        for dataFileFormat in dataFileFormats \
        for extension in dataFileFormat.extensions if isinstance(extension, str)
}
