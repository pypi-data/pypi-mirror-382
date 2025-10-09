from semantha_sdk.model import Reference
from semantha_sdk.semantha.ranking import RankingStrategy


class DenseOnly(RankingStrategy):
    def rank(
            self,
            dense_references: list[Reference],
            sparse_references: list[Reference]
    ):
        return dense_references
