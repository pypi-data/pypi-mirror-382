from typing import Optional

from semantha_sdk.model import Entity, DocumentInformation, Reference
from semantha_sdk.semantha import SemanthaDomain
from semantha_sdk.semantha.library.documentiter import DocumentIter
from semantha_sdk.semantha.library.documenttags import DocumentTags
from semantha_sdk.semantha.library.metadata import Metadata


class LibraryDocument:
    def __init__(
            self,
            domain: SemanthaDomain,
            document_id: Optional[str] = None,
            document: Optional[DocumentInformation] = None
    ):
        self.__api = domain.api()
        self.__domain = domain
        self.__domain_name = domain.name()

        if document_id is None and document is None:
            raise Exception("either document or document_id needs to be set")

        if document_id is None:
            document_id = document.id

        self.__document_id = document_id
        self.__reference_documents = self.__domain.reference_documents()
        self.__reference_document = self.__domain.reference_document(document_id)
        self.__references = self.__domain.references()

    @classmethod
    def from_document_id(cls, domain: SemanthaDomain, document_id: str):
        return cls(domain, document_id=document_id)

    @classmethod
    def from_document(cls, domain: SemanthaDomain, document: DocumentInformation):
        return cls(domain, document=document)

    @classmethod
    def from_reference(cls, domain: SemanthaDomain, reference: Reference):
        return cls.from_document_id(domain, document_id=reference.document_id)

    def get(self):
        return self.__reference_document.get()

    def id(self):
        return self.__reference_document.get().id

    def domain(self):
        return self.__domain

    def name(self):
        return self.__reference_document.get().name

    def document_class(self) -> Entity:
        return self.__reference_document.get().document_class

    def paragraph_by_id(self, paragraph_id: str) -> str:
        return self.__reference_document.paragraphs(id=paragraph_id).get().text

    def tags(self) -> DocumentTags:
        return DocumentTags(
            document_endpoint=self.__reference_document
        )

    def metadata(self):
        return Metadata(
            raw=self.get().metadata,
            reference_endpoint=self.__reference_document
        )

    def delete(self):
        self.__reference_document.delete()

    def iter(self) -> DocumentIter:
        """
        Builds an iterator over different parts of the document
        :return: the iterator object
        """
        return DocumentIter(
            document_endpoint=self.__reference_document
        )

    def paragraph_texts(self):
        """
        Iterates over each paragraph and collects the paragraph texts in a list
        :return: the list of paragraph texts
        """
        texts = []
        self.iter().for_each_paragraph(lambda page, paragraph: texts.append(paragraph.text))
        return texts

    def text(self):
        texts = self.paragraph_texts()
        return "\n".join(texts)
