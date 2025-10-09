from semantha_sdk.model.rule_function import RuleFunction
from semantha_sdk.model.rule_function import RuleFunctionSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ModelRulefunctionsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/rulefunctions"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/rulefunctions"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def get(
        self,
    ) -> List[RuleFunction]:
        """
        Get all rulecfunctions
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(RuleFunctionSchema)

    
    
    
    