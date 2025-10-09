from semantha_sdk.model.document_type import DocumentType
from semantha_sdk.model.document_type import DocumentTypeSchema
from semantha_sdk.model.name import Name
from semantha_sdk.model.name import NameSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class CloneEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/documenttypes/{id}/clone"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/clone"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    
    def post(
        self,
        body: Name = None,
    ) -> DocumentType:
        """
        Clone one document type and give it a new name. Needs roles: 'Advanced User', 'Domain Admin' or 'Expert User'
        Args:
        body (Name): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=NameSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(DocumentTypeSchema)

    
    
    