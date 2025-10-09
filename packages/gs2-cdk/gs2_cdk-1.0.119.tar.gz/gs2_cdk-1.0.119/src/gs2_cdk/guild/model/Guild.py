# Copyright 2016- Game Server Services, Inc. or its affiliates. All Rights
# Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
#
# deny overwrite
from __future__ import annotations
from typing import *

from ...core.model import CdkResource, Stack
from ...core.func import GetAttr
from .RoleModel import RoleModel

from ..ref.GuildRef import GuildRef
from .enums.GuildJoinPolicy import GuildJoinPolicy

from .options.GuildOptions import GuildOptions


class Guild(CdkResource):
    stack: Stack
    namespace_name: str
    user_id: str
    guild_model_name: str
    display_name: str
    join_policy: GuildJoinPolicy
    attribute1: Optional[int] = None
    attribute2: Optional[int] = None
    attribute3: Optional[int] = None
    attribute4: Optional[int] = None
    attribute5: Optional[int] = None
    metadata: Optional[str] = None
    member_metadata: Optional[str] = None
    custom_roles: Optional[List[RoleModel]] = None
    guild_member_default_role: Optional[str] = None
    time_offset_token: Optional[str] = None

    def __init__(
        self,
        stack: Stack,
        namespace_name: str,
        user_id: str,
        guild_model_name: str,
        display_name: str,
        join_policy: GuildJoinPolicy,
        options: Optional[GuildOptions] = GuildOptions(),
    ):
        super().__init__(
            "Guild_Guild_" + guild_model_name + ":" + name
        )

        self.stack = stack
        self.namespace_name = namespace_name
        self.user_id = user_id
        self.guild_model_name = guild_model_name
        self.display_name = display_name
        self.join_policy = join_policy
        self.attribute1 = options.attribute1 if options.attribute1 else None
        self.attribute2 = options.attribute2 if options.attribute2 else None
        self.attribute3 = options.attribute3 if options.attribute3 else None
        self.attribute4 = options.attribute4 if options.attribute4 else None
        self.attribute5 = options.attribute5 if options.attribute5 else None
        self.metadata = options.metadata if options.metadata else None
        self.member_metadata = options.member_metadata if options.member_metadata else None
        self.custom_roles = options.custom_roles if options.custom_roles else None
        self.guild_member_default_role = options.guild_member_default_role if options.guild_member_default_role else None
        self.time_offset_token = options.time_offset_token if options.time_offset_token else None
        stack.add_resource(
            self,
        )


    def alternate_keys(
        self,
    ):
        return self.guild_model_name + ":" + self.display_name

    def resource_type(
        self,
    ) -> str:
        return "GS2::Guild::Guild"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.namespace_name is not None:
            properties["NamespaceName"] = self.namespace_name
        if self.user_id is not None:
            properties["UserId"] = self.user_id
        if self.guild_model_name is not None:
            properties["GuildModelName"] = self.guild_model_name
        if self.display_name is not None:
            properties["DisplayName"] = self.display_name
        if self.attribute1 is not None:
            properties["Attribute1"] = self.attribute1
        if self.attribute2 is not None:
            properties["Attribute2"] = self.attribute2
        if self.attribute3 is not None:
            properties["Attribute3"] = self.attribute3
        if self.attribute4 is not None:
            properties["Attribute4"] = self.attribute4
        if self.attribute5 is not None:
            properties["Attribute5"] = self.attribute5
        if self.metadata is not None:
            properties["Metadata"] = self.metadata
        if self.member_metadata is not None:
            properties["MemberMetadata"] = self.member_metadata
        if self.join_policy is not None:
            properties["JoinPolicy"] = self.join_policy
        if self.custom_roles is not None:
            properties["CustomRoles"] = [
                v.properties(
                )
                for v in self.custom_roles
            ]
        if self.guild_member_default_role is not None:
            properties["GuildMemberDefaultRole"] = self.guild_member_default_role
        if self.time_offset_token is not None:
            properties["TimeOffsetToken"] = self.time_offset_token

        return properties

    def ref(
        self,
        name: str,
    ) -> GuildRef:
        return GuildRef(
            self.namespace_name,
            self.guild_model_name,
            name,
        )

    def get_attr_guild_id(
        self,
    ) -> GetAttr:
        return GetAttr(
            self,
            "Item.GuildId",
            None,
        )
