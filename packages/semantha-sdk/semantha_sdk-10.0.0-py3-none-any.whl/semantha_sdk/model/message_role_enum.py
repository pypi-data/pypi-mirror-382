from enum import Enum

class MessageRoleEnum(str, Enum):
    USER = "USER",
    ASSISTANT = "ASSISTANT",
    SYSTEM = "SYSTEM",
    
    def __str__(self) -> str:
        return self.value
