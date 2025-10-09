from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class Settings:
    """ author semantha, this is a generated class do not change manually! """
    similarity_model_id: Optional[str] = None
    smart_cluster_similarity_model_id: Optional[str] = None
    smart_cluster_max_items: Optional[int] = None
    compare_library_max_items: Optional[int] = None
    analyzer_max_items: Optional[int] = None
    keep_numbers: Optional[bool] = None
    min_tokens: Optional[int] = None
    similarity_measure: Optional[str] = None
    paragraph_reference_strategy: Optional[str] = None
    context_weight: Optional[float] = None
    enable_string_comparison: Optional[bool] = None
    enable_paragraph_length_comparison: Optional[bool] = None
    enable_whitespace_diff: Optional[bool] = None
    default_document_type: Optional[str] = None
    enable_paragraph_sorting: Optional[bool] = None
    enable_paragraph_end_detection: Optional[bool] = None
    enable_boost_word_filtering_for_input_documents: Optional[bool] = None
    tagging_similarity_mode: Optional[str] = None
    enable_updating_fingerprints_on_tag_updates: Optional[bool] = None
    enable_paragraph_merging_based_on_formatting: Optional[bool] = None
    use_creation_date_from_input_document: Optional[bool] = None
    enable_saturated_match_colors: Optional[bool] = None
    enable_no_match_color_red: Optional[bool] = None
    enable_context_consideration: Optional[bool] = None
    enable_paragraph_resizing: Optional[bool] = None
    similarity_max_deviation: Optional[int] = None
    enable_tagging: Optional[bool] = None
    tagging_threshold: Optional[float] = None
    tagging_strategy: Optional[str] = None
    extraction_threshold: Optional[float] = None
    extraction_strategy: Optional[str] = None
    resize_paragraphs_on_extraction: Optional[bool] = None
    relevant_page_count: Optional[int] = None
    enable_gpt: Optional[bool] = None
    max_number_of_pages: Optional[int] = None
    max_number_of_rows: Optional[int] = None
    language: Optional[str] = None
    default_similarity_mode: Optional[str] = None

SettingsSchema = class_schema(Settings, base_schema=RestSchema)
