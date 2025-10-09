from semantha_sdk.model.transaction_summary import TransactionSummary
from semantha_sdk.model.transaction_summary import TransactionSummarySchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class TransactionsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/transactions"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/transactions"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def get(
        self,
        startdate: str = None,
        enddate: str = None,
    ) -> List[TransactionSummary]:
        """
        Returns a summary of document transactions for a given day interval. Needs role: 'Domain Admin'
        Args:
        startdate str: Start date of the day interval, inclusive that day. Format is: yyyy-mm-dd
    enddate str: End date of the day interval, excluse that day. Format is: yyyy-mm-dd
        """
        q_params = {}
        if startdate is not None:
            q_params["startdate"] = startdate
        if enddate is not None:
            q_params["enddate"] = enddate
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(TransactionSummarySchema)

    
    
    
    