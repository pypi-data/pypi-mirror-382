from semantha_sdk.model.extractor_class import ExtractorClass
from semantha_sdk.model.extractor_class import ExtractorClassSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ChildExtractorclassesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/extractorclasses/{id}/extractorclasses"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/extractorclasses"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    
    def post(
        self,
        body: ExtractorClass = None,
    ) -> ExtractorClass:
        """
        
        Args:
        body (ExtractorClass): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=ExtractorClassSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(ExtractorClassSchema)

    
    
    