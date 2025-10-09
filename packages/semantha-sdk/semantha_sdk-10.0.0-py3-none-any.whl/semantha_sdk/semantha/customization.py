from semantha_sdk import SemanthaAPI
from semantha_sdk.model import Synonym, BoostWord


class Customization:
    def __init__(self, api: SemanthaAPI, domain: str):
        self.__api = api
        self.__domain_model = self.__api.model.domains(domain)
        self.__synonyms = self.__domain_model.synonyms
        self.__boost_words = self.__domain_model.boostwords

    def add_synonym(
            self,
            word: str,
            synonym: str
    ) -> Synonym:
        return self.__synonyms.post(Synonym(
            id=None,
            word=word,
            synonym=synonym,
            regex=None,
            tags=None
        ))

    def delete_synonym(
            self,
            synonym: Synonym
    ):
        self.__synonyms(synonym.id).delete()

    def add_boost_word(
            self,
            word: str
    ):
        self.__boost_words.post(BoostWord(
            id=None,
            word=word,
            regex=None,
            tags=None,
            label=None
        ))

    def delete_boost_word(
            self,
            boost_word: BoostWord,
    ):
        self.__boost_words(boost_word.id).delete()
