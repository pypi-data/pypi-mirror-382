from typing import Callable

from semantha_sdk.api.referencedocument import ReferencedocumentEndpoint
from semantha_sdk.model import Paragraph, Page, Reference


class DocumentIter:
    __reference_document: ReferencedocumentEndpoint

    def __init__(
            self,
            document_endpoint: ReferencedocumentEndpoint
    ):
        self.__reference_document = document_endpoint

    def paragraphs(self):
        all_paragraphs = []

        doc = self.__reference_document.get()

        for idx, page in enumerate(doc.pages):
            if page.contents is None:
                continue

            for content in page.contents:
                if content.paragraphs is None:
                    break

                for paragraph in content.paragraphs:
                    all_paragraphs.append((idx, paragraph))

        return all_paragraphs

    def for_each_paragraph(self, fn: Callable[[int, Paragraph], None]):
        """
        Executes the given callable for every paragraph in the document
        :param fn: the lambda/function to be called
        """
        for idx, paragraph in self.paragraphs():
            fn(idx, paragraph)

    def pages(self):
        doc = self.__reference_document.get()

        return doc.pages

    def for_each_page(self, fn: Callable[[int, Page], None]):
        """
        Executes the given callable for each page of this library entry
        :param fn: the lambda/function to be called for each page
        """
        for idx, page in enumerate(self.pages()):
            fn(idx, page)

    def for_each_paragraph_reference(self, fn: Callable[[int, Paragraph, Reference], None]):
        """
        Executes the given callable for each paragraph reference of this library entry
        :param fn: the lambda/function to be called for each reference
        """

        def for_each_ref(page: int, paragraph: Paragraph):
            if paragraph.references is None:
                return

            for ref in paragraph.references:
                fn(page, paragraph, ref)

        self.for_each_paragraph(for_each_ref)
