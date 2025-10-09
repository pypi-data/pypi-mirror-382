from semantha_sdk.model.data_property import DataProperty
from semantha_sdk.model.data_property import DataPropertySchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class BulkmodelDatapropertiesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/bulk/model/domains/{domainname}/dataproperties"
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

    def get(
        self,
    ) -> List[DataProperty]:
        """
        Get all dataproperties
            This is the quiet version of  'get /api/domains/{domainname}/dataproperties'
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(DataPropertySchema)

    def post(
        self,
        body: List[DataProperty] = None,
    ) -> None:
        """
        Create one or more dataproperties
            This is the quiet version of  'post /api/domains/{domainname}/dataproperties'
        Args:
        body (List[DataProperty]): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=DataPropertySchema().dump(body, many=True),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.as_none()

    
    
    