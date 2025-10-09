import abc

from semantha_sdk.model import Reference


class RankingStrategy(abc.ABC):
    def __init__(
            self,
            alpha: float
    ):
        self.__alpha = alpha

    @abc.abstractmethod
    def rank(
            self,
            dense_references: list[Reference],
            sparse_references: list[Reference]
    ) -> list[Reference]:
        pass
