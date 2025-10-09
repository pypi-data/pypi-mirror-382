from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.document_information import DocumentInformation
from semantha_sdk.model.response_meta_info import ResponseMetaInfo
from typing import List
from typing import Optional

@dataclass
class ReferenceDocumentsResponseContainer:
    """ author semantha, this is a generated class do not change manually! """
    meta: Optional[ResponseMetaInfo] = None
    data: Optional[List[DocumentInformation]] = None

ReferenceDocumentsResponseContainerSchema = class_schema(ReferenceDocumentsResponseContainer, base_schema=RestSchema)
