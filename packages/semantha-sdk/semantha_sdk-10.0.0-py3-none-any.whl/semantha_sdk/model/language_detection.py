from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema


@dataclass
class LanguageDetection:
    """ author semantha, this is a generated class do not change manually! """
    language: str

LanguageDetectionSchema = class_schema(LanguageDetection, base_schema=RestSchema)
