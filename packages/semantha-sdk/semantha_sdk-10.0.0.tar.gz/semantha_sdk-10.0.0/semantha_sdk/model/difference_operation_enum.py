from enum import Enum

class DifferenceOperationEnum(str, Enum):
    DELETE = "DELETE",
    INSERT = "INSERT",
    EQUAL = "EQUAL",
    
    def __str__(self) -> str:
        return self.value
