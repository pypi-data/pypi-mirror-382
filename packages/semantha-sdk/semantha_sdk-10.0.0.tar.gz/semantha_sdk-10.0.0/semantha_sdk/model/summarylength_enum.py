from enum import Enum

class SummarylengthEnum(str, Enum):
    SHORT = "SHORT",
    MEDIUM = "MEDIUM",
    LONG = "LONG",
    
    def __str__(self) -> str:
        return self.value
