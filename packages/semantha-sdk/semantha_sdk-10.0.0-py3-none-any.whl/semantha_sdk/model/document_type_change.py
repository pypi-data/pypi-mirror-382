from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.area import Area
from semantha_sdk.model.custom_field import CustomField
from typing import List
from typing import Optional

@dataclass
class DocumentTypeChange:
    """ author semantha, this is a generated class do not change manually! """
    name: Optional[str] = None
    do_object_detection: Optional[bool] = None
    do_sub_document_splitting: Optional[bool] = None
    split_modus: Optional[str] = None
    split_by_type: Optional[str] = None
    split_by_regex: Optional[str] = None
    use_similarity_model_for_extraction: Optional[bool] = None
    do_paragraph_merging_for_text_files: Optional[bool] = None
    ignored_pages: Optional[List[int]] = None
    viewport: Optional[Area] = None
    custom_fields: Optional[List[CustomField]] = None

DocumentTypeChangeSchema = class_schema(DocumentTypeChange, base_schema=RestSchema)
