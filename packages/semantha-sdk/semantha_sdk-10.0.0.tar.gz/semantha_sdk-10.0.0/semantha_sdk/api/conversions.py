from io import IOBase
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ConversionsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/conversions"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/conversions"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    
    def post(
        self,
        file: IOBase = None,
    ) -> IOBase:
        """
        
            Converts docx files into pdf format.
        Args:
        file (IOBase): The document to convert.
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
            },
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.as_bytesio()

    
    
    