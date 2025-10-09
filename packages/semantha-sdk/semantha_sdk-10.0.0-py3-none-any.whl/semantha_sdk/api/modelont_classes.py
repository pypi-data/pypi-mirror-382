from semantha_sdk.api.modelont_class import ModelontClassEndpoint
from semantha_sdk.model.classes_overview import ClassesOverview
from semantha_sdk.model.classes_overview import ClassesOverviewSchema
from semantha_sdk.model.clazz import Clazz
from semantha_sdk.model.clazz import ClazzSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ModelontClassesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/classes"
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
    ) -> ModelontClassEndpoint:
        return ModelontClassEndpoint(self._session, self._endpoint, classid)

    def get(
        self,
        withattributes: bool = None,
        withobjectproperties: bool = None,
    ) -> List[ClassesOverview]:
        """
        Get all classes
        Args:
        withattributes bool: Select if the classes are delivered with attributes
    withobjectproperties bool: Select if the classes are delivered with object properties
        """
        q_params = {}
        if withattributes is not None:
            q_params["withattributes"] = withattributes
        if withobjectproperties is not None:
            q_params["withobjectproperties"] = withobjectproperties
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(ClassesOverviewSchema)

    def post(
        self,
        body: Clazz = None,
    ) -> Clazz:
        """
        Create a class
        Args:
        body (Clazz): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=ClazzSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(ClazzSchema)

    
    def delete(
        self,
    ) -> None:
        """
        Delete all classes
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    