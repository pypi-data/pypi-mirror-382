from enum import Enum

class FieldTypeEnum(str, Enum):
    CLASS = "CLASS",
    OBJECT_PROPERTY = "OBJECT_PROPERTY",
    DATA_PROPERTY = "DATA_PROPERTY",
    
    def __str__(self) -> str:
        return self.value
