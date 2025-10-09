from semantha_sdk.api.modelont_attributes import ModelontAttributesEndpoint
from semantha_sdk.api.modelontclass_instances import ModelontclassInstancesEndpoint
from semantha_sdk.model.clazz import Clazz
from semantha_sdk.model.clazz import ClazzSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ModelontClassEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/classes/{classid}"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + f"/{self._classid}"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
        classid: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
        self._classid = classid
        self.__attributes = ModelontAttributesEndpoint(session, self._endpoint)
        self.__instances = ModelontclassInstancesEndpoint(session, self._endpoint)

    @property
    def attributes(self) -> ModelontAttributesEndpoint:
        return self.__attributes

    @property
    def instances(self) -> ModelontclassInstancesEndpoint:
        return self.__instances

    def get(
        self,
    ) -> Clazz:
        """
        
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(ClazzSchema)

    
    
    def delete(
        self,
    ) -> None:
        """
        
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    def put(
        self,
        body: Clazz
    ) -> Clazz:
        """
        
        """
        return self._session.put(
            url=self._endpoint,
            json=ClazzSchema().dump(body)
        ).execute().to(ClazzSchema)
