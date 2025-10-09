from semantha_sdk.api.answers import AnswersEndpoint
from semantha_sdk.api.chats import ChatsEndpoint
from semantha_sdk.api.documentannotations import DocumentannotationsEndpoint
from semantha_sdk.api.documentclasses import DocumentclassesEndpoint
from semantha_sdk.api.documents import DocumentsEndpoint
from semantha_sdk.api.documenttypes import DocumenttypesEndpoint
from semantha_sdk.api.modelclasses import ModelclassesEndpoint
from semantha_sdk.api.modelinstances import ModelinstancesEndpoint
from semantha_sdk.api.prompts import PromptsEndpoint
from semantha_sdk.api.referencedocuments import ReferencedocumentsEndpoint
from semantha_sdk.api.references import ReferencesEndpoint
from semantha_sdk.api.settings import SettingsEndpoint
from semantha_sdk.api.summarizations import SummarizationsEndpoint
from semantha_sdk.api.tags import TagsEndpoint
from semantha_sdk.api.texttypes import TexttypesEndpoint
from semantha_sdk.api.transactions import TransactionsEndpoint
from semantha_sdk.api.validation import ValidationEndpoint
from semantha_sdk.model.domain import Domain
from semantha_sdk.model.domain import DomainSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class DomainEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + f"/{self._domainname}"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
        domainname: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
        self._domainname = domainname
        self.__answers = AnswersEndpoint(session, self._endpoint)
        self.__chats = ChatsEndpoint(session, self._endpoint)
        self.__documentannotations = DocumentannotationsEndpoint(session, self._endpoint)
        self.__documentclasses = DocumentclassesEndpoint(session, self._endpoint)
        self.__documents = DocumentsEndpoint(session, self._endpoint)
        self.__documenttypes = DocumenttypesEndpoint(session, self._endpoint)
        self.__modelclasses = ModelclassesEndpoint(session, self._endpoint)
        self.__modelinstances = ModelinstancesEndpoint(session, self._endpoint)
        self.__prompts = PromptsEndpoint(session, self._endpoint)
        self.__referencedocuments = ReferencedocumentsEndpoint(session, self._endpoint)
        self.__references = ReferencesEndpoint(session, self._endpoint)
        self.__settings = SettingsEndpoint(session, self._endpoint)
        self.__summarizations = SummarizationsEndpoint(session, self._endpoint)
        self.__tags = TagsEndpoint(session, self._endpoint)
        self.__texttypes = TexttypesEndpoint(session, self._endpoint)
        self.__transactions = TransactionsEndpoint(session, self._endpoint)
        self.__validation = ValidationEndpoint(session, self._endpoint)

    @property
    def answers(self) -> AnswersEndpoint:
        return self.__answers

    @property
    def chats(self) -> ChatsEndpoint:
        return self.__chats

    @property
    def documentannotations(self) -> DocumentannotationsEndpoint:
        return self.__documentannotations

    @property
    def documentclasses(self) -> DocumentclassesEndpoint:
        return self.__documentclasses

    @property
    def documents(self) -> DocumentsEndpoint:
        return self.__documents

    @property
    def documenttypes(self) -> DocumenttypesEndpoint:
        return self.__documenttypes

    @property
    def modelclasses(self) -> ModelclassesEndpoint:
        return self.__modelclasses

    @property
    def modelinstances(self) -> ModelinstancesEndpoint:
        return self.__modelinstances

    @property
    def prompts(self) -> PromptsEndpoint:
        return self.__prompts

    @property
    def referencedocuments(self) -> ReferencedocumentsEndpoint:
        return self.__referencedocuments

    @property
    def references(self) -> ReferencesEndpoint:
        return self.__references

    @property
    def settings(self) -> SettingsEndpoint:
        return self.__settings

    @property
    def summarizations(self) -> SummarizationsEndpoint:
        return self.__summarizations

    @property
    def tags(self) -> TagsEndpoint:
        return self.__tags

    @property
    def texttypes(self) -> TexttypesEndpoint:
        return self.__texttypes

    @property
    def transactions(self) -> TransactionsEndpoint:
        return self.__transactions

    @property
    def validation(self) -> ValidationEndpoint:
        return self.__validation

    def get(
        self,
    ) -> Domain:
        """
        Get the configuration settings of a specific domain.
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(DomainSchema)

    
    
    
    