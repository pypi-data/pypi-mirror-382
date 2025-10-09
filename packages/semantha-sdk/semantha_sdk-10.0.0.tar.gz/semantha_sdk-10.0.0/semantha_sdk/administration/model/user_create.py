from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import List
from typing import Optional

@dataclass
class UserCreate:
    """ author semantha, this is a generated class do not change manually! """
    email: str
    enabled: Optional[bool] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    two_factor_enabled: Optional[bool] = None
    roles: Optional[List[str]] = None
    domain_roles: Optional[List[str]] = None
    app_roles: Optional[List[str]] = None

UserCreateSchema = class_schema(UserCreate, base_schema=RestSchema)
