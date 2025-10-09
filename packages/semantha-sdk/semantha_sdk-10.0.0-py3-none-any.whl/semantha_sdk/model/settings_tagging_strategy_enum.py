from enum import Enum

class SettingsTagging_strategyEnum(str, Enum):
    TOP1 = "TOP1",
    TOP3 = "TOP3",
    TOP5 = "TOP5",
    TOP10 = "TOP10",
    
    def __str__(self) -> str:
        return self.value
