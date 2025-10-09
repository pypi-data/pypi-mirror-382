from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.settings import Settings

@dataclass
class Domain:
    """ author semantha, this is a generated class do not change manually! """
    id: str
    name: str
    settings: Settings

DomainSchema = class_schema(Domain, base_schema=RestSchema)
