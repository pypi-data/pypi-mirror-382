from semantha_sdk.model.document_information import DocumentInformation
from semantha_sdk.model.document_information import DocumentInformationSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class TagReferencedocumentsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/tags/{tagname}/referencedocuments"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/referencedocuments"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def get(
        self,
    ) -> List[DocumentInformation]:
        """
        Get all reference documents with a specific tag
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(DocumentInformationSchema)

    
    
    def delete(
        self,
    ) -> None:
        """
        Delete reference documents with a specific tag
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    