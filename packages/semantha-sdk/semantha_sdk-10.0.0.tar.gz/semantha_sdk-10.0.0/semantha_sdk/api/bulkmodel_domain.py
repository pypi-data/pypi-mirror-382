from semantha_sdk.api.bulkmodel_boostwords import BulkmodelBoostwordsEndpoint
from semantha_sdk.api.bulkmodel_classes import BulkmodelClassesEndpoint
from semantha_sdk.api.bulkmodel_dataproperties import BulkmodelDatapropertiesEndpoint
from semantha_sdk.api.bulkmodel_instances import BulkmodelInstancesEndpoint
from semantha_sdk.api.bulkmodel_metadata import BulkmodelMetadataEndpoint
from semantha_sdk.api.bulkmodel_namedentities import BulkmodelNamedentitiesEndpoint
from semantha_sdk.api.bulkmodel_rules import BulkmodelRulesEndpoint
from semantha_sdk.api.bulkmodel_stopwords import BulkmodelStopwordsEndpoint
from semantha_sdk.api.bulkmodel_synonyms import BulkmodelSynonymsEndpoint
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class BulkmodelDomainEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/bulk/model/domains/{domainname}"
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
        self.__boostwords = BulkmodelBoostwordsEndpoint(session, self._endpoint)
        self.__classes = BulkmodelClassesEndpoint(session, self._endpoint)
        self.__dataproperties = BulkmodelDatapropertiesEndpoint(session, self._endpoint)
        self.__instances = BulkmodelInstancesEndpoint(session, self._endpoint)
        self.__metadata = BulkmodelMetadataEndpoint(session, self._endpoint)
        self.__namedentities = BulkmodelNamedentitiesEndpoint(session, self._endpoint)
        self.__rules = BulkmodelRulesEndpoint(session, self._endpoint)
        self.__stopwords = BulkmodelStopwordsEndpoint(session, self._endpoint)
        self.__synonyms = BulkmodelSynonymsEndpoint(session, self._endpoint)

    @property
    def boostwords(self) -> BulkmodelBoostwordsEndpoint:
        return self.__boostwords

    @property
    def classes(self) -> BulkmodelClassesEndpoint:
        return self.__classes

    @property
    def dataproperties(self) -> BulkmodelDatapropertiesEndpoint:
        return self.__dataproperties

    @property
    def instances(self) -> BulkmodelInstancesEndpoint:
        return self.__instances

    @property
    def metadata(self) -> BulkmodelMetadataEndpoint:
        return self.__metadata

    @property
    def namedentities(self) -> BulkmodelNamedentitiesEndpoint:
        return self.__namedentities

    @property
    def rules(self) -> BulkmodelRulesEndpoint:
        return self.__rules

    @property
    def stopwords(self) -> BulkmodelStopwordsEndpoint:
        return self.__stopwords

    @property
    def synonyms(self) -> BulkmodelSynonymsEndpoint:
        return self.__synonyms

    
    
    
    
    