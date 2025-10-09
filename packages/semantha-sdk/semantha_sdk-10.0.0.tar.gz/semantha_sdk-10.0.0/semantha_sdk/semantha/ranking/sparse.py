from semantha_sdk.model import Reference
from semantha_sdk.semantha.ranking import RankingStrategy


class SparseFilter(RankingStrategy):
    def rank(
            self,
            dense_references: list[Reference],
            sparse_references: list[Reference]
    ) -> list[Reference]:
        if len(dense_references) == 0:
            return dense_references

        sparse_ids = [ref.document_id for ref in sparse_references]

        return [ref for ref in dense_references if ref.document_id in sparse_ids]
