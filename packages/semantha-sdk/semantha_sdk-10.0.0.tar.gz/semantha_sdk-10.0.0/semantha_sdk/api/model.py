from semantha_sdk.api.model_datatypes import ModelDatatypesEndpoint
from semantha_sdk.api.model_domains import ModelDomainsEndpoint
from semantha_sdk.api.model_extractortypes import ModelExtractortypesEndpoint
from semantha_sdk.api.model_metadatatypes import ModelMetadatatypesEndpoint
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ModelEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/model"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
        self.__datatypes = ModelDatatypesEndpoint(session, self._endpoint)
        self.__domains = ModelDomainsEndpoint(session, self._endpoint)
        self.__extractortypes = ModelExtractortypesEndpoint(session, self._endpoint)
        self.__metadatatypes = ModelMetadatatypesEndpoint(session, self._endpoint)

    @property
    def datatypes(self) -> ModelDatatypesEndpoint:
        return self.__datatypes

    @property
    def domains(self) -> ModelDomainsEndpoint:
        return self.__domains

    @property
    def extractortypes(self) -> ModelExtractortypesEndpoint:
        return self.__extractortypes

    @property
    def metadatatypes(self) -> ModelMetadatatypesEndpoint:
        return self.__metadatatypes

    
    
    
    
    