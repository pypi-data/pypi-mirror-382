from semantha_sdk.semantha import SemanthaDomain
from semantha_sdk.semantha.library import LibraryDocument


class Tags:
    def __init__(
            self,
            domain: SemanthaDomain
    ):
        self.__domain = domain
        self.__tags = domain.domain().tags

    def all(self) -> list[str]:
        return self.__tags.get()

    def documents_with_tag(self, tag: str) -> list[LibraryDocument]:
        return [
            LibraryDocument.from_document_id(
                domain=self.__domain,
                document_id=doc.id
            ) for doc in self.__tags(tagname=tag).referencedocuments.get()
        ]
