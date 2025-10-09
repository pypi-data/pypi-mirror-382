from semantha_sdk.model.paragraph import Paragraph
from semantha_sdk.model.paragraph import ParagraphSchema
from semantha_sdk.model.paragraph_update import ParagraphUpdate
from semantha_sdk.model.paragraph_update import ParagraphUpdateSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ParagraphEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/referencedocuments/{documentid}/paragraphs/{id}"
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

    def get(
        self,
    ) -> Paragraph:
        """
        Get one paragraph of a specific document.
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(ParagraphSchema)

    
    def patch(
        self,
        body: ParagraphUpdate
    ) -> Paragraph:
        """
        Update one paragraph of a specific document. Needs roles: 'Domain Admin' or 'Expert User'
        """
        return self._session.patch(
            url=self._endpoint,
            json=ParagraphUpdateSchema().dump(body)
        ).execute().to(ParagraphSchema)

    def delete(
        self,
    ) -> None:
        """
        Delete one paragraph of a specific document. Needs roles: 'Domain Admin' or 'Expert User'
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    