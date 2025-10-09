from semantha_sdk.api.domain import DomainEndpoint
from semantha_sdk.model import Settings


class DomainSettings:
    __domain: DomainEndpoint

    def __init__(self, domain: DomainEndpoint):
        self.__domain = domain

    def change_model(self, model_id: str):
        settings = self.__domain.settings.patch(Settings(similarity_model_id=str(model_id)))
        return int(settings.similarity_model_id)
