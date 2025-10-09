import io
import json
import os
from io import IOBase, BytesIO
from typing import Type, Optional

from semantha_sdk import SemanthaAPI
from semantha_sdk.api.documents import DocumentsEndpoint
from semantha_sdk.api.referencedocuments import ReferencedocumentsEndpoint
from semantha_sdk.api.references import ReferencesEndpoint
from semantha_sdk.model import Reference
from semantha_sdk.semantha import SemanthaDomain
from semantha_sdk.semantha.files import _to_text_file
from semantha_sdk.semantha.library.document import LibraryDocument
from semantha_sdk.semantha.library.tags import Tags
from semantha_sdk.semantha.ranking import RankingStrategy
from semantha_sdk.semantha.ranking.dense import DenseOnly


class Library:
    __domain_name: str

    __api: SemanthaAPI
    __domain: SemanthaDomain
    __documents: DocumentsEndpoint
    __references: ReferencesEndpoint
    __reference_documents: ReferencedocumentsEndpoint

    def __init__(
            self,
            domain: SemanthaDomain,
    ):
        self.__api = domain.api()
        self.__domain = domain
        self.__domain_name = domain.name()
        self.__documents = domain.documents()
        self.__references = domain.references()
        self.__reference_documents = domain.reference_documents()

    @classmethod
    def for_domain(cls, domain: SemanthaDomain):
        return cls(
            domain=domain
        )

    def upload_file(
            self,
            document: IOBase,
            metadata: Optional[dict[str, any] | str] = None,
            tags: Optional[list[str]] = None,
    ) -> LibraryDocument:
        """
        Uploads a document as a file object to the library
        :param document: the file to be uploaded
        :return: the uploaded document
        """
        metadata = json.dumps(metadata) if isinstance(metadata, dict) else metadata
        tags = ",".join(tags)

        document = self.__reference_documents.post(
            file=document,
            metadata=metadata,
            tags=tags,
        )[0]
        return LibraryDocument.from_document(
            self.__domain,
            document
        )

    def upload_text(
            self,
            text: str,
            metadata: Optional[dict[str, any] | str] = None,
            tags: Optional[list[str]] = None,
    ):
        """
        Uploads a text document to the library
        :param text: the text to be uploaded
        :return: the uploaded document
        """
        if tags is None:
            tags = []

        metadata = json.dumps(metadata) if isinstance(metadata, dict) else metadata
        tags = None if tags is None else ",".join(tags) if len(tags) else None

        document = self.__reference_documents.post(
            text=text,
            metadata=metadata,
            tags=tags
        )[0]
        return LibraryDocument.from_document(
            self.__domain,
            document,
        )

    def upload_folder(self, path: str) -> list[LibraryDocument]:
        """
        Uploads all files at the given path to the library
        :param path: the path to traverse for files
        :return: the list of uploaded documents
        """
        # TODO: bulk endpoint?
        documents = []
        for path in os.listdir(path):
            with open(path, mode="rb") as file:
                document = self.upload_file(BytesIO(file.read()))
                documents.append(document)

        return documents

    def delete_all(self):
        self.__reference_documents.delete()

    def documents_with_tag(self, tag: str):
        return self.tags().get_documents_with_tag(tag)

    def tags(self) -> Tags:
        return Tags(self.__domain)

    def reference_document(self, reference: Reference) -> LibraryDocument:
        """
        Fetches the document for a given reference
        :param reference: the reference
        :return: the document
        """
        doc = self.__reference_documents(reference.document_id).get()
        return LibraryDocument.from_document(
            domain=self.__domain,
            document=doc
        )

    def sparse_references(self, text_or_file: str | io.IOBase):
        """
        Fetches the sparse (mode=document) references for a given text or file
        :param text_or_file: the text or file
        :return: the references
        """
        if text_or_file is io.IOBase:
            return self.__references.post(
                mode="document",
                file=text_or_file
            ).references

        if text_or_file is str:
            return self.__references.post(
                mode="document",
                text=text_or_file
            ).references

    def dense_references(self, text_or_file: str | io.IOBase):
        """
        Fetches the dense (mode=fingerprint) references for a given text or file
        :param text_or_file:
        :return:
        """
        if text_or_file is io.IOBase:
            return self.__references.post(
                mode="fingerprint",
                file=text_or_file
            ).references

        if text_or_file is str:
            return self.__references.post(
                mode="fingerprint",
                text=text_or_file
            ).references

    def document_by_id(self, id: str):
        """
        Fetches a specific document by id
        :param id: the id to look for
        :return: the document
        """
        doc = self.__reference_documents(id).get()
        return LibraryDocument.from_document(
            domain=self.__domain,
            document=doc
        )

    def documents_by_ids(self, ids: list[str]):
        """
        Fetches a list of document by given ids
        :param ids: the list of ids
        :return: the list of documents
        """
        response = self.__reference_documents.get(
            offset=0,
            limit=len(ids),
            documentids=",".join(ids)
        )

        return [
            LibraryDocument.from_document_id(
                domain=self.__domain,
                document_id=doc.id
            )
            for doc in response.data
        ]

    def documents_with_tags(self, tags: list[str], offset: int = 0, limit: int = 50):
        """
        Fetches a list of documents that have all given tags
        :param tags: the tags to filter with
        :param offset: offset of results
        :param limit: limit of results
        :return:
        """
        docs = self.__reference_documents.get(
            tags="+".join(tags),
            offset=offset,
            limit=limit
        )

        return [LibraryDocument.from_document(
            domain=self.__domain,
            document=doc
        ) for doc in docs.data]

    def query_with_ranking(
            self,
            text: str,
            ranking: Type[RankingStrategy] = DenseOnly
    ):
        ranker = ranking(alpha=0.7)

        dense_refs = self.dense_references(text)
        sparse_refs = self.sparse_references(text)

        ranked = ranker.rank(dense_refs, sparse_refs)

        return ranked

    def metadata_as_dict(self, document_id: str) -> dict:
        """
        Fetches the metadata of a document and returns it as a dict
        :param document_id:
        :return:
        """
        doc = self.__reference_documents(document_id).get()
        return json.loads(doc.metadata)

    def _reference_document_for_text(
            self,
            text: str,
            reference_text: Optional[str] = None,
            tags: list[str] = None,
            threshold: float = 0.8,
            max_matches: int = 10,
            mode: str = "fingerprint",
            document_type: Optional[str] = None
    ):
        doc = self.__references.post(
            file=_to_text_file(text),
            referencedocument=_to_text_file(reference_text) if reference_text is not None else None,
            similaritythreshold=threshold,
            maxreferences=max_matches,
            tags="+".join(tags),
            mode=mode,
            documenttype=document_type
        )
        return (LibraryDocument.from_document(
            self.__domain,
            doc
        ), doc.references)

    def references_for_text(
            self,
            text: str,
            reference_text: Optional[str] = None,
            tags: list[str] = None,
            threshold: float = 0.8,
            max_matches: int = 10,
            mode: str = "fingerprint",
            document_type: Optional[str] = None
    ) -> list[Reference] | None:
        if tags is None:
            tags = []

        doc, references = self._reference_document_for_text(
            text,
            reference_text,
            tags,
            threshold,
            max_matches,
            mode,
            document_type
        )

        return references

    def paragraph_references_for_text(
            self,
            text: str,
            reference_text: Optional[str] = None,
            tags: list[str] = None,
            threshold: float = 0.8,
            max_matches: int = 10,
            mode: str = "fingerprint",
            document_type: Optional[str] = None
    ) -> list[Reference]:
        doc, references = self._reference_document_for_text(
            text,
            reference_text,
            tags,
            threshold,
            max_matches,
            mode,
            document_type
        )

        references = []

        doc.for_each_paragraph(lambda page, paragraph: references.append(paragraph.references))

        return [ref for refs in references for ref in refs]
