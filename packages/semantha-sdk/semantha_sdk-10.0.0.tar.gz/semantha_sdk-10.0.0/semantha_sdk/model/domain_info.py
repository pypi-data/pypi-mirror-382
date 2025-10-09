from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema


@dataclass
class DomainInfo:
    """ author semantha, this is a generated class do not change manually! """
    id: str
    name: str
    base_url: str

DomainInfoSchema = class_schema(DomainInfo, base_schema=RestSchema)
