from semantha_sdk.api.model_dataproperty import ModelDatapropertyEndpoint
from semantha_sdk.model.data_property import DataProperty
from semantha_sdk.model.data_property import DataPropertySchema
from semantha_sdk.model.overview import Overview
from semantha_sdk.model.overview import OverviewSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ModelDatapropertiesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/dataproperties"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/dataproperties"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def __call__(
            self,
            id: str,
    ) -> ModelDatapropertyEndpoint:
        return ModelDatapropertyEndpoint(self._session, self._endpoint, id)

    def get(
        self,
    ) -> List[Overview]:
        """
        Read all available entities.
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(OverviewSchema)

    def post(
        self,
        body: DataProperty = None,
    ) -> DataProperty:
        """
        Create a new entity. Needs roles: 'Domain Admin' or 'Expert User'
        Args:
        body (DataProperty): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=DataPropertySchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(DataPropertySchema)

    
    def delete(
        self,
    ) -> None:
        """
        Delete all available entities. Needs roles: 'Domain Admin' or 'Expert User'
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    