from typing import Optional

import semantha_sdk
from semantha_sdk import SemanthaAPI
from semantha_sdk.semantha.compare import Compare
from semantha_sdk.semantha.domain import SemanthaDomain
from semantha_sdk.semantha.library import Library

_SUMMARIZATION_STOP_TOKENS = ["References:", "Reference"]


class Semantha():
    __current_domain: Optional[SemanthaDomain] = None

    def __init__(self, semantha_api: SemanthaAPI, domain_name: Optional[str] = None):
        """
        Creates a new instance of the high level semantha use-case SDK
        :param semantha_api: the low level semantha API client
        :param domain_name: the domain to use, if not given and only one domain is available that domain will be
            chosen as default.
        """
        self.__api = semantha_api

        if domain_name is not None:
            self.__domain = self.__api.domains(domain_name)
            self.__domain_name = domain_name
            self.__domain_model = self.__api.model.domains(domain_name)

            self.__current_domain = SemanthaDomain.from_domain(
                self.__api,
                self.__domain.get()
            )

    @staticmethod
    def login(
            server_url: str,
            domain: Optional[str] = None,
            key: Optional[str] = None,
            key_file: Optional[str] = None,
    ) -> "Semantha":
        """
        Logs in to the semantha platform at a given url
        :param server_url: the semantha platform server url
        :param domain: the domain to use for this semantha instance
        :param key: your api key
        :param key_file: path to a file containing your api key
        :return:
        """
        return login(
            server_url, domain, key, key_file
        )

    def api(self) -> SemanthaAPI:
        """
        Access to the low level semantha api.
        :return: the low level semantha api instance
        """
        return self.__api

    def current_domain(self) -> Optional[SemanthaDomain]:
        return self.__current_domain

    def available_domains(self) -> list[SemanthaDomain]:
        """
        Lists all domains available for the stored api key
        :return: list of domain objects
        """
        domains = self.__api.domains.get()
        return [SemanthaDomain.from_domain(self.__api, domain) for domain in domains]

    def domain(self, domain_name: str) -> Optional[SemanthaDomain]:
        """
        Fetches a domain by name
        :param domain_name: the domain to fetch
        :return: the domain, if it exists
        """
        domain = self.__api.domains(domain_name).get()
        return SemanthaDomain.from_domain(
            api=self.__api,
            domain=domain
        )

    def set_domain(self, domain_name: str) -> "Semantha":
        """
        Sets the current domain for this instance by name
        :param domain_name: the name of the domain to use
        :return: the same semantha instance with the new domain set
        """
        domain = self.domain(domain_name)

        if domain is None:
            return self

        self.__current_domain = domain

        return self

    def library(self):
        """
        Creates a new library instance for the domain of this semantha instance
        :return:
        """
        if self.__current_domain is None:
            raise Exception("Please set a domain first")

        return Library.for_domain(self.__current_domain)

    def compare(self):
        """
        Creates a new compare service instance for the domain of this semantha instance
        :return:
        """
        if self.__current_domain is None:
            raise Exception("Please set a domain first")

        return Compare.for_domain(self.__current_domain)

    # def summarize(self, sources: list[str], topic: str) -> str:
    #     sources_with_refs = [f"[{idx + 1}] {source}" for idx, source in enumerate(sources)]
    #     response = self.__domain.summarizations.post(
    #         texts=sources_with_refs,
    #         topic=topic
    #     )
    #
    #     for token in _SUMMARIZATION_STOP_TOKENS:
    #         response = response.split(token, maxsplit=1)[0]
    #
    #     return response.rstrip()


def login(server_url: str, domain: str, key: str = None, key_file: str = None) -> Semantha:
    __api = semantha_sdk.login(server_url, key, key_file)
    return Semantha(__api, domain)
