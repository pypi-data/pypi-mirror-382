from __future__ import annotations

from io import IOBase

from semantha_sdk.api.bulk import BulkEndpoint
from semantha_sdk.api.celltypes import CelltypesEndpoint
from semantha_sdk.api.conversions import ConversionsEndpoint
from semantha_sdk.api.currentuser import CurrentuserEndpoint
from semantha_sdk.api.diff import DiffEndpoint
from semantha_sdk.api.domains import DomainsEndpoint
from semantha_sdk.api.info import InfoEndpoint
from semantha_sdk.api.languages import LanguagesEndpoint
from semantha_sdk.api.model import ModelEndpoint
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint


class SemanthaAPI(RestEndpoint):
    """ Entry point to the Semantha API.

        author semantha, this is a generated class do not change manually!
        Calls the /bulk, /celltypes, /conversions, /currentuser, /diff, /domains, /info, /languages, /model,  endpoints.

        Note:
            The __init__ method is not meant to be invoked directly
            use `login()` with your credentials instead.
    """

    def __init__(self, session: RestClient, parent_endpoint: str):
        super().__init__(session, parent_endpoint)
        self.__bulk = BulkEndpoint(session, self._endpoint)
        self.__celltypes = CelltypesEndpoint(session, self._endpoint)
        self.__conversions = ConversionsEndpoint(session, self._endpoint)
        self.__currentuser = CurrentuserEndpoint(session, self._endpoint)
        self.__diff = DiffEndpoint(session, self._endpoint)
        self.__domains = DomainsEndpoint(session, self._endpoint)
        self.__info = InfoEndpoint(session, self._endpoint)
        self.__languages = LanguagesEndpoint(session, self._endpoint)
        self.__model = ModelEndpoint(session, self._endpoint)

    @property
    def _endpoint(self):
        return self._parent_endpoint

    @property
    def bulk(self) -> BulkEndpoint:
        return self.__bulk

    @property
    def celltypes(self) -> CelltypesEndpoint:
        return self.__celltypes

    @property
    def conversions(self) -> ConversionsEndpoint:
        return self.__conversions

    @property
    def currentuser(self) -> CurrentuserEndpoint:
        return self.__currentuser

    @property
    def diff(self) -> DiffEndpoint:
        return self.__diff

    @property
    def domains(self) -> DomainsEndpoint:
        return self.__domains

    @property
    def info(self) -> InfoEndpoint:
        return self.__info

    @property
    def languages(self) -> LanguagesEndpoint:
        return self.__languages

    @property
    def model(self) -> ModelEndpoint:
        return self.__model

