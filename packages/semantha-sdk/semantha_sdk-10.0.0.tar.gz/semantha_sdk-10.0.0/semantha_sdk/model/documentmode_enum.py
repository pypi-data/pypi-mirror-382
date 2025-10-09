from enum import Enum

class DocumentmodeEnum(str, Enum):
    sentence = "sentence",
    paragraph = "paragraph",
    
    def __str__(self) -> str:
        return self.value
