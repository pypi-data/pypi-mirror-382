from io import IOBase
from semantha_sdk.administration.model.import_information import ImportInformation
from semantha_sdk.administration.model.import_information import ImportInformationSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class TransportEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/administration/domains/{domainname}/transport"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/transport"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def get_as_zip(
        self,
        withextraction: bool = None,
        withlanguagemodel: bool = None,
        withconfiguration: bool = None,
        withlibrary: bool = None,
        withlibrarysentences: bool = None,
        withdocumentannotation: bool = None,
        withsimilaritymodelid: bool = None,
    ) -> IOBase:
        """
        
        Args:
        withextraction bool: 
    withlanguagemodel bool: 
    withconfiguration bool: 
    withlibrary bool: 
    withlibrarysentences bool: 
    withdocumentannotation bool: 
    withsimilaritymodelid bool: 
        """
        q_params = {}
        if withextraction is not None:
            q_params["withextraction"] = withextraction
        if withlanguagemodel is not None:
            q_params["withlanguagemodel"] = withlanguagemodel
        if withconfiguration is not None:
            q_params["withconfiguration"] = withconfiguration
        if withlibrary is not None:
            q_params["withlibrary"] = withlibrary
        if withlibrarysentences is not None:
            q_params["withlibrarysentences"] = withlibrarysentences
        if withdocumentannotation is not None:
            q_params["withdocumentannotation"] = withdocumentannotation
        if withsimilaritymodelid is not None:
            q_params["withsimilaritymodelid"] = withsimilaritymodelid
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.ZIP)).execute().as_bytesio()

    def post(
        self,
        body: IOBase = None,
    ) -> ImportInformation:
        """
        
        Args:
        body (IOBase): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            body={
                "body": body,
            },
            headers=RestClient.to_header(MediaType.JSON, "application/zip"),
            q_params=q_params
        ).execute()
        return response.to(ImportInformationSchema)

    
    
    