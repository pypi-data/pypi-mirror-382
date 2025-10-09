from __future__ import annotations

from io import IOBase

from semantha_sdk.administration.administration import AdministrationEndpoint
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint


class AdministrationAPI(RestEndpoint):
    """ Entry point to the Administration API.

        author semantha, this is a generated class do not change manually!
        Calls the /administration,  endpoints.

        Note:
            The __init__ method is not meant to be invoked directly
            use `login()` with your credentials instead.
    """

    def __init__(self, session: RestClient, parent_endpoint: str):
        super().__init__(session, parent_endpoint)
        self.__administration = AdministrationEndpoint(session, self._endpoint)

    @property
    def _endpoint(self):
        return self._parent_endpoint

    @property
    def administration(self) -> AdministrationEndpoint:
        return self.__administration

