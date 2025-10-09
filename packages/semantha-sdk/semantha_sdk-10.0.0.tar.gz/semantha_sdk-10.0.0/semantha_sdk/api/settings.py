from semantha_sdk.model.settings import Settings
from semantha_sdk.model.settings import SettingsSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class SettingsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/settings"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/settings"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def get(
        self,
        withsimilaritymodelid: bool = None,
    ) -> Settings:
        """
        Get the configuration settings of a specific domain.
        Args:
        withsimilaritymodelid bool: If true, similarityModelId and smartClusterSimilarityModelId are returned.
        """
        q_params = {}
        if withsimilaritymodelid is not None:
            q_params["withsimilaritymodelid"] = withsimilaritymodelid
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(SettingsSchema)

    
    def patch(
        self,
        body: Settings
    ) -> Settings:
        """
        Update configuration settings for this domain, e.g. which similarity model to use. Needs roles: 'Domain Admin' or 'Expert User'
        """
        return self._session.patch(
            url=self._endpoint,
            json=SettingsSchema().dump(body)
        ).execute().to(SettingsSchema)

    
    