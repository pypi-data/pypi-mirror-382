from enum import Enum

class TypeEnum(str, Enum):
    similarity = "similarity",
    extraction = "extraction",
    
    def __str__(self) -> str:
        return self.value
