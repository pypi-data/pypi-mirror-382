from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ModelBackupsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/backups"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/backups"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    
    def post(
        self,
    ) -> None:
        """
        Create a backup for the ontology
        Args:
            """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            body={
            },
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.as_none()

    
    
    