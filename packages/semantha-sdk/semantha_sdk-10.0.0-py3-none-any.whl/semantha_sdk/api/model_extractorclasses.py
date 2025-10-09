from semantha_sdk.api.model_extractorclass import ModelExtractorclassEndpoint
from semantha_sdk.model.extractor_class import ExtractorClass
from semantha_sdk.model.extractor_class import ExtractorClassSchema
from semantha_sdk.model.extractor_class_overview import ExtractorClassOverview
from semantha_sdk.model.extractor_class_overview import ExtractorClassOverviewSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ModelExtractorclassesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/extractorclasses"
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

    def __call__(
            self,
            id: str,
    ) -> ModelExtractorclassEndpoint:
        return ModelExtractorclassEndpoint(self._session, self._endpoint, id)

    def get(
        self,
    ) -> List[ExtractorClassOverview]:
        """
        Read all available entities.
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(ExtractorClassOverviewSchema)

    def post(
        self,
        body: ExtractorClass = None,
    ) -> ExtractorClass:
        """
        Create a new entity. Needs roles: 'Domain Admin' or 'Expert User'
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

    
    def delete(
        self,
    ) -> None:
        """
        Delete all available entities. Needs roles: 'Domain Admin' or 'Expert User'
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    def put(
        self,
        body: List[ExtractorClassOverview]
    ) -> None:
        """
        
        """
        return self._session.put(
            url=self._endpoint,
            json=ExtractorClassOverviewSchema().dump(body, many=True)
        ).execute().as_none()
