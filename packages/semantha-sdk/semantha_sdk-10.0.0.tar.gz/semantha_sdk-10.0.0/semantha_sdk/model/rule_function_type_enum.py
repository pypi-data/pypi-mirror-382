from enum import Enum

class RuleFunctionTypeEnum(str, Enum):
    OPERATOR = "OPERATOR",
    FUNCTION = "FUNCTION",
    
    def __str__(self) -> str:
        return self.value
