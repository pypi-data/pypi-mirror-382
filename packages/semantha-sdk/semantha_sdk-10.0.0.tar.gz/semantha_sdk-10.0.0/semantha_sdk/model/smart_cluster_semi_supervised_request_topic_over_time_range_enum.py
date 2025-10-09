from enum import Enum

class SmartClusterSemiSupervisedRequestTopic_over_time_rangeEnum(str, Enum):
    HOURS = "HOURS",
    DAYS = "DAYS",
    MONTHS = "MONTHS",
    YEARS = "YEARS",
    
    def __str__(self) -> str:
        return self.value
