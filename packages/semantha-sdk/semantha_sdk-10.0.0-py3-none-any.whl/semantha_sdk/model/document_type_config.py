from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.area import Area
from typing import List
from typing import Optional

@dataclass
class DocumentTypeConfig:
    """ author semantha, this is a generated class do not change manually! """
    do_linebased_processing: Optional[bool] = None
    viewport: Optional[Area] = None
    ignored_pages: Optional[List[int]] = None
    do_language_detection: Optional[bool] = None
    do_object_detection: Optional[bool] = None
    do_sub_document_splitting: Optional[bool] = None
    split_modus: Optional[str] = None
    split_by_type: Optional[str] = None
    split_by_regex: Optional[str] = None
    based_on_document_type: Optional[str] = None
    do_auto_splitting: Optional[bool] = None
    auto_split_distance: Optional[float] = None
    use_similarity_model_for_extraction: Optional[bool] = None
    do_paragraph_merging_for_text_files: Optional[bool] = None

DocumentTypeConfigSchema = class_schema(DocumentTypeConfig, base_schema=RestSchema)
