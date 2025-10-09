from enum import Enum

class ClassBulkDatatypeEnum(str, Enum):
    STRING = "STRING",
    CURRENCY = "CURRENCY",
    DATE = "DATE",
    NUMBER = "NUMBER",
    YEAR = "YEAR",
    BOOLEAN = "BOOLEAN",
    INTEGER = "INTEGER",
    
    def __str__(self) -> str:
        return self.value
