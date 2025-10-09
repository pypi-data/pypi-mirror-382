from enum import Enum

class SettingsDefault_similarity_modeEnum(str, Enum):
    fingerprint = "fingerprint",
    keyword = "keyword",
    document = "document",
    document_fingerprint = "document_fingerprint",
    fingerprint_keyword = "fingerprint_keyword",
    auto = "auto",
    
    def __str__(self) -> str:
        return self.value
