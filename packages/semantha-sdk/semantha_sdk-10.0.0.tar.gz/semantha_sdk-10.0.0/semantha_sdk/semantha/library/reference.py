from semantha_sdk.model import Reference
from semantha_sdk.semantha import SemanthaDomain


class LibraryReference:
    def __init__(self, domain: SemanthaDomain, reference: Reference):
        self.__api = domain.api()
        self.__reference = reference
        self.__domain = domain

    def get_document(self):
        """
        Fetches the corresponding document for this reference
        :return: the document corresponding to this reference
        """
        return self.__domain.reference_document(self.__reference.document_id).get()

    @classmethod
    def from_reference_id(cls, reference_id: str):
        pass

    @classmethod
    def from_reference(cls, domain: SemanthaDomain, reference: Reference):
        return LibraryReference(domain, reference)
