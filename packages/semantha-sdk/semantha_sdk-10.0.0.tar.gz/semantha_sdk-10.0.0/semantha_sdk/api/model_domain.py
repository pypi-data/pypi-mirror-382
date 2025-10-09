from io import IOBase
from semantha_sdk.api.model_attributes import ModelAttributesEndpoint
from semantha_sdk.api.model_backups import ModelBackupsEndpoint
from semantha_sdk.api.model_boostwords import ModelBoostwordsEndpoint
from semantha_sdk.api.model_dataproperties import ModelDatapropertiesEndpoint
from semantha_sdk.api.model_extractorclasses import ModelExtractorclassesEndpoint
from semantha_sdk.api.model_extractors import ModelExtractorsEndpoint
from semantha_sdk.api.model_formatters import ModelFormattersEndpoint
from semantha_sdk.api.model_metadata import ModelMetadataEndpoint
from semantha_sdk.api.model_namedentities import ModelNamedentitiesEndpoint
from semantha_sdk.api.model_objectproperties import ModelObjectpropertiesEndpoint
from semantha_sdk.api.model_regexes import ModelRegexesEndpoint
from semantha_sdk.api.model_relations import ModelRelationsEndpoint
from semantha_sdk.api.model_rulefunctions import ModelRulefunctionsEndpoint
from semantha_sdk.api.model_rules import ModelRulesEndpoint
from semantha_sdk.api.model_stopwords import ModelStopwordsEndpoint
from semantha_sdk.api.model_synonyms import ModelSynonymsEndpoint
from semantha_sdk.api.modelont_classes import ModelontClassesEndpoint
from semantha_sdk.api.modelont_instances import ModelontInstancesEndpoint
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ModelDomainEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}"
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
        self.__attributes = ModelAttributesEndpoint(session, self._endpoint)
        self.__backups = ModelBackupsEndpoint(session, self._endpoint)
        self.__boostwords = ModelBoostwordsEndpoint(session, self._endpoint)
        self.__classes = ModelontClassesEndpoint(session, self._endpoint)
        self.__dataproperties = ModelDatapropertiesEndpoint(session, self._endpoint)
        self.__extractorclasses = ModelExtractorclassesEndpoint(session, self._endpoint)
        self.__extractors = ModelExtractorsEndpoint(session, self._endpoint)
        self.__formatters = ModelFormattersEndpoint(session, self._endpoint)
        self.__instances = ModelontInstancesEndpoint(session, self._endpoint)
        self.__metadata = ModelMetadataEndpoint(session, self._endpoint)
        self.__namedentities = ModelNamedentitiesEndpoint(session, self._endpoint)
        self.__objectproperties = ModelObjectpropertiesEndpoint(session, self._endpoint)
        self.__regexes = ModelRegexesEndpoint(session, self._endpoint)
        self.__relations = ModelRelationsEndpoint(session, self._endpoint)
        self.__rulefunctions = ModelRulefunctionsEndpoint(session, self._endpoint)
        self.__rules = ModelRulesEndpoint(session, self._endpoint)
        self.__stopwords = ModelStopwordsEndpoint(session, self._endpoint)
        self.__synonyms = ModelSynonymsEndpoint(session, self._endpoint)

    @property
    def attributes(self) -> ModelAttributesEndpoint:
        return self.__attributes

    @property
    def backups(self) -> ModelBackupsEndpoint:
        return self.__backups

    @property
    def boostwords(self) -> ModelBoostwordsEndpoint:
        return self.__boostwords

    @property
    def classes(self) -> ModelontClassesEndpoint:
        return self.__classes

    @property
    def dataproperties(self) -> ModelDatapropertiesEndpoint:
        return self.__dataproperties

    @property
    def extractorclasses(self) -> ModelExtractorclassesEndpoint:
        return self.__extractorclasses

    @property
    def extractors(self) -> ModelExtractorsEndpoint:
        return self.__extractors

    @property
    def formatters(self) -> ModelFormattersEndpoint:
        return self.__formatters

    @property
    def instances(self) -> ModelontInstancesEndpoint:
        return self.__instances

    @property
    def metadata(self) -> ModelMetadataEndpoint:
        return self.__metadata

    @property
    def namedentities(self) -> ModelNamedentitiesEndpoint:
        return self.__namedentities

    @property
    def objectproperties(self) -> ModelObjectpropertiesEndpoint:
        return self.__objectproperties

    @property
    def regexes(self) -> ModelRegexesEndpoint:
        return self.__regexes

    @property
    def relations(self) -> ModelRelationsEndpoint:
        return self.__relations

    @property
    def rulefunctions(self) -> ModelRulefunctionsEndpoint:
        return self.__rulefunctions

    @property
    def rules(self) -> ModelRulesEndpoint:
        return self.__rules

    @property
    def stopwords(self) -> ModelStopwordsEndpoint:
        return self.__stopwords

    @property
    def synonyms(self) -> ModelSynonymsEndpoint:
        return self.__synonyms

    def get_as_xlsx(
        self,
    ) -> IOBase:
        """
        Get a domain by domainname
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.XLSX)).execute().as_bytesio()

    
    def patch(
        self,
        file: IOBase
    ) -> IOBase:
        """
        Update a domain by domainname
        """
        return self._session.patch(
            url=self._endpoint,
            json=file
        ).execute().as_bytesio()

    
    