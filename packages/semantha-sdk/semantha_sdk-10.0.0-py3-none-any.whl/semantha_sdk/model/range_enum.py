from enum import Enum

class RangeEnum(str, Enum):
    HOURS = "HOURS",
    DAYS = "DAYS",
    MONTHS = "MONTHS",
    YEARS = "YEARS",
    
    def __str__(self) -> str:
        return self.value
