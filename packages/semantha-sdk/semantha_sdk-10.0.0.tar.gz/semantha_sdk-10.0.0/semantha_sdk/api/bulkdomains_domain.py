from semantha_sdk.api.bulkdomains_documentclasses import BulkdomainsDocumentclassesEndpoint
from semantha_sdk.api.bulkdomains_documenttypes import BulkdomainsDocumenttypesEndpoint
from semantha_sdk.api.bulkdomains_referencedocuments import BulkdomainsReferencedocumentsEndpoint
from semantha_sdk.api.bulkdomains_references import BulkdomainsReferencesEndpoint
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class BulkdomainsDomainEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/bulk/domains/{domainname}"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + f"/{self._domainname}"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
        domainname: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
        self._domainname = domainname
        self.__documentclasses = BulkdomainsDocumentclassesEndpoint(session, self._endpoint)
        self.__documenttypes = BulkdomainsDocumenttypesEndpoint(session, self._endpoint)
        self.__referencedocuments = BulkdomainsReferencedocumentsEndpoint(session, self._endpoint)
        self.__references = BulkdomainsReferencesEndpoint(session, self._endpoint)

    @property
    def documentclasses(self) -> BulkdomainsDocumentclassesEndpoint:
        return self.__documentclasses

    @property
    def documenttypes(self) -> BulkdomainsDocumenttypesEndpoint:
        return self.__documenttypes

    @property
    def referencedocuments(self) -> BulkdomainsReferencedocumentsEndpoint:
        return self.__referencedocuments

    @property
    def references(self) -> BulkdomainsReferencesEndpoint:
        return self.__references

    
    
    
    
    