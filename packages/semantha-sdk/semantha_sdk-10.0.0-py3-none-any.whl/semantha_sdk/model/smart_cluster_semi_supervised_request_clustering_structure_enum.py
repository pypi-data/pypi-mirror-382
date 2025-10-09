from enum import Enum

class SmartClusterSemiSupervisedRequestClustering_structureEnum(str, Enum):
    LOCAL = "LOCAL",
    BALANCED = "BALANCED",
    GLOBAL = "GLOBAL",
    
    def __str__(self) -> str:
        return self.value
