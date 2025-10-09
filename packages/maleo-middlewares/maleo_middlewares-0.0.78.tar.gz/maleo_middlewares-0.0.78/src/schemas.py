from pydantic import BaseModel, Field
from typing import Annotated, List
from uuid import UUID
from maleo.enums.organization import OrganizationType
from maleo.enums.status import DataStatus as DataStatusEnum
from maleo.enums.system import Role
from maleo.enums.user import UserType
from maleo.schemas.mixins.identity import DataIdentifier
from maleo.schemas.mixins.status import DataStatus
from maleo.types.string import ListOfStrings
from maleo.types.uuid import OptionalUUID


class InactiveKeys(BaseModel):
    keys: ListOfStrings = Field(..., min_length=1, description="Inactive keys")


class SystemRole(DataStatus[DataStatusEnum], DataIdentifier):
    system_role: Annotated[Role, Field(..., description="System role")]


class User(DataStatus[DataStatusEnum], DataIdentifier):
    user_type: Annotated[UserType, Field(..., description="User's type")]
    username: Annotated[str, Field(..., description="User's username", max_length=50)]
    email: Annotated[str, Field(..., description="User's email", max_length=255)]
    system_roles: Annotated[
        List[SystemRole], Field(..., description="User's system roles", min_length=1)
    ]


class Organization(DataStatus[DataStatusEnum], DataIdentifier):
    organization_type: Annotated[
        OrganizationType, Field(..., description="Organization's type")
    ]


class UserOrganization(DataStatus[DataStatusEnum], DataIdentifier):
    user_id: Annotated[int, Field(..., description="User's ID", ge=1)]
    organization_id: Annotated[int, Field(..., description="Organization's ID", ge=1)]
    user_organization_roles: Annotated[
        ListOfStrings, Field(..., description="User's organization roles", min_length=1)
    ]


class UserOrganizationId(BaseModel):
    user_id: Annotated[UUID, Field(..., description="User's ID")]
    organization_id: Annotated[
        OptionalUUID, Field(None, description="Organization's ID")
    ] = None
