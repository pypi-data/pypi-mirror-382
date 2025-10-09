from semantha_sdk.model.model_class import ModelClass
from semantha_sdk.model.model_class import ModelClassSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ModelclassesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/modelclasses"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/modelclasses"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def get(
        self,
        uilanguage: str = None,
    ) -> List[ModelClass]:
        """
        Get all model classes
        Args:
        uilanguage str: Selects the language of the labels in the JSON response; useful with multi-language domain models.
        """
        q_params = {}
        if uilanguage is not None:
            q_params["uilanguage"] = uilanguage
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(ModelClassSchema)

    
    
    
    