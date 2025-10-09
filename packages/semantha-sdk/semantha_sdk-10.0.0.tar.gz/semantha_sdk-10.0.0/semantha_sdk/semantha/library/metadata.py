import json

from semantha_sdk.api.referencedocument import ReferencedocumentEndpoint
from semantha_sdk.model import DocumentInformation


class Metadata:
    __raw: str | None

    def __init__(
            self,
            raw: str,
            reference_endpoint: ReferencedocumentEndpoint
    ):
        self.__raw = raw
        self.__reference_document = reference_endpoint

    def as_dict(self) -> dict | None:
        """
        Attempts to parse the metadata as a JSON dictionary.
        :return: the decoded dict if the string represents a JSON dictionary, None otherwise
        """
        if self.__raw is None:
            return None

        try:
            value = json.loads(self.__raw)
        except json.JSONDecodeError:
            return None

        return value if isinstance(value, dict) else None

    def as_str(self) -> str | None:
        """
        Returns the metadata as a string
        :return: the metadata string
        """
        return self.__raw

    def update(self, value: dict):
        """
        Replaces the document metadata with the given dictionary (as json)
        :param value: the dictionary
        :return:
        """
        self.__reference_document.patch(DocumentInformation(metadata=json.dumps(value)))
