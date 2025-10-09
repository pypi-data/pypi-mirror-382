from io import IOBase
from semantha_sdk.model.semantic_model import SemanticModel
from semantha_sdk.model.semantic_model import SemanticModelSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ValidationEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/validation"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/validation"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    
    def post(
        self,
        file: IOBase = None,
    ) -> SemanticModel:
        """
        Validate existing data in a document
            The coordinates come back, if data is found
        Args:
        file (IOBase): Input document (left document).
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
            },
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(SemanticModelSchema)

    
    
    