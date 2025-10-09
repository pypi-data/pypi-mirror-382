from io import IOBase

from semantha_sdk.api.references import ReferencesEndpoint
from semantha_sdk.semantha.domain import SemanthaDomain
from semantha_sdk.semantha.files import _to_text_file


class Compare:
    __references: ReferencesEndpoint

    def __init__(
            self,
            domain: SemanthaDomain
    ):
        self.__api = domain.api()
        self.__domain = domain.domain()

    @classmethod
    def for_domain(cls, domain: SemanthaDomain):
        return cls(
            domain
        )

    def compare_texts(
            self,
            text_a: str,
            text_b: str,
            threshold: float = 0.01
    ) -> float:
        """
        Directly compare two texts
        :param text_a: the first text
        :param text_b: the second text
        :param threshold: the threshold to use
        :return: the similarity
        """
        return self.compare_files(
            file_a=_to_text_file(text_a),
            file_b=_to_text_file(text_b),
            threshold=threshold
        )

    def compare_files(
            self,
            file_a: IOBase,
            file_b: IOBase,
            threshold: float = 0.01
    ):
        """
        Directly compare two files
        :param file_a: the first file
        :param file_b: the second file
        :param threshold: the threshold to use
        :return: the similarity
        """
        __doc = self.__references.post(
            file=file_a,
            referencedocument=file_b,
            similaritythreshold=threshold,
            maxreferences=1
        )

        if __doc.references:
            return __doc.references[0].similarity

        return 0.0
