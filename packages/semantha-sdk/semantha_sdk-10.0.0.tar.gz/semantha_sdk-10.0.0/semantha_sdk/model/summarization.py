from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class Summarization:
    """ author semantha, this is a generated class do not change manually! """
    summary: Optional[str] = None

SummarizationSchema = class_schema(Summarization, base_schema=RestSchema)
