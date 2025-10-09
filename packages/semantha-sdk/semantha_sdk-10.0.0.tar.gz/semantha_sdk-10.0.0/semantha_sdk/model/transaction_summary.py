from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema


@dataclass
class TransactionSummary:
    """ author semantha, this is a generated class do not change manually! """
    number_of_documents: int
    number_of_pages: int
    service: str

TransactionSummarySchema = class_schema(TransactionSummary, base_schema=RestSchema)
