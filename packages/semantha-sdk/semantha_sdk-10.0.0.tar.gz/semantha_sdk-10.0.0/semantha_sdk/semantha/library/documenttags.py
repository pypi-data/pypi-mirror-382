from semantha_sdk.api.referencedocument import ReferencedocumentEndpoint
from semantha_sdk.model import DocumentInformation


class DocumentTags:
    def __init__(
            self,
            document_endpoint: ReferencedocumentEndpoint
    ):
        self.__reference_document = document_endpoint

    def add(self, tag: str):
        """
        Adds a tag to this library entry
        :param tag: the tag to add
        :return: the document with the tag added
        """
        doc = self.__reference_document.get()
        return self.__reference_document.patch(DocumentInformation(
            tags=doc.tags + [tag]
        ))

    def remove(self, tag: str):
        """
        Removes a given tag from the document if it exists
        :param tag: the tag to be removed
        :return: the document with the tag removed
        """
        doc = self.__reference_document.get()

        if tag in doc.tags:
            doc.tags.remove(tag)

        return self.__reference_document.patch(DocumentInformation(
            tags=doc.tags
        ))

    def all(self):
        doc = self.__reference_document.get()
        return doc.tags + doc.derived_tags
