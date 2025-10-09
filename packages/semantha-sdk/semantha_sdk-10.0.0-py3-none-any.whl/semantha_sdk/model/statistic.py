from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.tag_docs import TagDocs
from typing import List
from typing import Optional

@dataclass
class Statistic:
    """ author semantha, this is a generated class do not change manually! """
    library_size: int
    size: int
    number_of_sentences: int
    docs_per_tag: Optional[List[TagDocs]] = None

StatisticSchema = class_schema(Statistic, base_schema=RestSchema)
