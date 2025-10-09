from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.extraction_file import ExtractionFile
from semantha_sdk.model.model_instance import ModelInstance
from semantha_sdk.model.process_information import ProcessInformation
from semantha_sdk.model.table_instance import TableInstance
from typing import List
from typing import Optional

@dataclass
class SemanticModel:
    """ author semantha, this is a generated class do not change manually! """
    files: Optional[List[ExtractionFile]] = None
    instances: Optional[List[ModelInstance]] = None
    tables: Optional[List[TableInstance]] = None
    process_information: Optional[ProcessInformation] = None

SemanticModelSchema = class_schema(SemanticModel, base_schema=RestSchema)
