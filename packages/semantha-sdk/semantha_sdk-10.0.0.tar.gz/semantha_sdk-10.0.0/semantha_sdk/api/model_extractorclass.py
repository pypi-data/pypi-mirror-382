from semantha_sdk.api.child_extractorclasses import ChildExtractorclassesEndpoint
from semantha_sdk.model.extractor_class import ExtractorClass
from semantha_sdk.model.extractor_class import ExtractorClassSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ModelExtractorclassEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/extractorclasses/{id}"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + f"/{self._id}"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
        id: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
        self._id = id
        self.__extractorclasses = ChildExtractorclassesEndpoint(session, self._endpoint)

    @property
    def extractorclasses(self) -> ChildExtractorclassesEndpoint:
        return self.__extractorclasses

    def get(
        self,
    ) -> ExtractorClass:
        """
        Read one entity.
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(ExtractorClassSchema)

    
    
    def delete(
        self,
    ) -> None:
        """
        Delete one entity. Needs roles: 'Domain Admin' or 'Expert User'
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    def put(
        self,
        body: ExtractorClass
    ) -> ExtractorClass:
        """
        Change one entity. Needs roles: 'Domain Admin' or 'Expert User'
        """
        return self._session.put(
            url=self._endpoint,
            json=ExtractorClassSchema().dump(body)
        ).execute().to(ExtractorClassSchema)
