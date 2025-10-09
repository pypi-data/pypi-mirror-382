from semantha_sdk.model import Reference
from semantha_sdk.semantha.ranking import RankingStrategy


class Hybrid(RankingStrategy):
    def rank(
            self,
            dense_references: list[Reference],
            sparse_references: list[Reference]
    ) -> list[Reference]:
        if len(dense_references) == 0:
            return dense_references

        sparse_ids = [ref.document_id for ref in sparse_references]

        scoring: list[(float, Reference)] = []

        for idx, ref in enumerate(dense_references):
            rank = sparse_ids.index(ref.document_id) if ref.document_id in sparse_ids else None
            score = (1 / (idx + 1)) + (
                0 if rank is None else (self.__alpha * (1 / (rank + 1)))
            )
            scoring.append((score, ref))

        scoring.sort(key=lambda tup: tup[0], reverse=True)

        return [ref for _, ref in scoring]
