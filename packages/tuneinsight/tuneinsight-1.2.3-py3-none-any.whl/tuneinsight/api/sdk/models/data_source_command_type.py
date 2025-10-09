from enum import Enum


class DataSourceCommandType(str, Enum):
    GENERICCOMMAND = "genericCommand"
    GETMETADATACOMMAND = "getMetadataCommand"
    GETCONCEPTMETADATACOMMAND = "getConceptMetadataCommand"
    GETCONCEPTFIELDVALUESCOMMAND = "getConceptFieldValuesCommand"

    def __str__(self) -> str:
        return str(self.value)
