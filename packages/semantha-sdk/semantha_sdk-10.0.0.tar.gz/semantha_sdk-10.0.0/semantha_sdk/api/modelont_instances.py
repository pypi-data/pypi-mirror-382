from io import IOBase
from semantha_sdk.api.modelont_instance import ModelontInstanceEndpoint
from semantha_sdk.model.instance import Instance
from semantha_sdk.model.instance import InstanceSchema
from semantha_sdk.model.instance_overview import InstanceOverview
from semantha_sdk.model.instance_overview import InstanceOverviewSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ModelontInstancesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/instances"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/instances"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def __call__(
            self,
            id: str,
    ) -> ModelontInstanceEndpoint:
        return ModelontInstanceEndpoint(self._session, self._endpoint, id)

    def get(
        self,
    ) -> List[InstanceOverview]:
        """
        Read all available entities.
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(InstanceOverviewSchema)
    def get_as_xlsx(
        self,
    ) -> IOBase:
        """
        Read all available entities.
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.XLSX)).execute().as_bytesio()

    def post(
        self,
        body: Instance = None,
    ) -> Instance:
        """
        Create a new entity. Needs roles: 'Domain Admin' or 'Expert User'
        Args:
        body (Instance): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=InstanceSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(InstanceSchema)

    def patch(
        self,
        file: IOBase
    ) -> None:
        """
        Update all instances
        """
        return self._session.patch(
            url=self._endpoint,
            json=file
        ).execute().as_none()

    def delete(
        self,
    ) -> None:
        """
        Delete all available entities. Needs roles: 'Domain Admin' or 'Expert User'
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    