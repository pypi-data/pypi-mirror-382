from semantha_sdk.model.text_type import TextType
from semantha_sdk.model.text_type import TextTypeSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class TexttypesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/texttypes"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/texttypes"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def get(
        self,
    ) -> List[TextType]:
        """
        Returns all available text types.
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(TextTypeSchema)

    
    def patch(
        self,
        body: List[TextType]
    ) -> None:
        """
        Saves text types, order of elements determines display order. Needs roles: 'Domain Admin' or 'Expert User'
        """
        return self._session.patch(
            url=self._endpoint,
            json=TextTypeSchema().dump(body, many=True)
        ).execute().as_none()

    def delete(
        self,
    ) -> None:
        """
        Resets changes made via PATCH calls. Needs roles: 'Domain Admin' or 'Expert User'
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    