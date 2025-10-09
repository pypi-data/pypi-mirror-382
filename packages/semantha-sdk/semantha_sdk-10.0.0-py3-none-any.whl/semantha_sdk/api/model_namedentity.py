from semantha_sdk.model.named_entity import NamedEntity
from semantha_sdk.model.named_entity import NamedEntitySchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ModelNamedentityEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/namedentities/{id}"
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
    ) -> NamedEntity:
        """
        Read one entity.
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(NamedEntitySchema)

    
    
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
        body: NamedEntity
    ) -> NamedEntity:
        """
        Change one entity. Needs roles: 'Domain Admin' or 'Expert User'
        """
        return self._session.put(
            url=self._endpoint,
            json=NamedEntitySchema().dump(body)
        ).execute().to(NamedEntitySchema)
