from semantha_sdk.api.bulkmodel_class import BulkmodelClassEndpoint
from semantha_sdk.model.class_bulk import ClassBulk
from semantha_sdk.model.class_bulk import ClassBulkSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class BulkmodelClassesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/bulk/model/domains/{domainname}/classes"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/classes"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def __call__(
            self,
            classid: str,
    ) -> BulkmodelClassEndpoint:
        return BulkmodelClassEndpoint(self._session, self._endpoint, classid)

    def get(
        self,
    ) -> List[ClassBulk]:
        """
        Get all classes
            This is the quiet version of  'get /api/domains/{domainname}/classes'
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(ClassBulkSchema)

    def post(
        self,
        body: List[ClassBulk] = None,
    ) -> None:
        """
        Create one or more classes
            This is the quiet version of  'post /api/domains/{domainname}/classes'
        Args:
        body (List[ClassBulk]): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=ClassBulkSchema().dump(body, many=True),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.as_none()

    
    
    