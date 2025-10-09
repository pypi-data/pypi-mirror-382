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
from __future__ import annotations
from typing import *
from .RoleModel import RoleModel
from .options.GuildModelOptions import GuildModelOptions


class GuildModel:
    name: str
    default_maximum_member_count: int
    maximum_member_count: int
    inactivity_period_days: int
    roles: List[RoleModel]
    guild_master_role: str
    guild_member_default_role: str
    rejoin_cool_time_minutes: int
    metadata: Optional[str] = None
    max_concurrent_join_guilds: Optional[int] = None
    max_concurrent_guild_master_count: Optional[int] = None

    def __init__(
        self,
        name: str,
        default_maximum_member_count: int,
        maximum_member_count: int,
        inactivity_period_days: int,
        roles: List[RoleModel],
        guild_master_role: str,
        guild_member_default_role: str,
        rejoin_cool_time_minutes: int,
        options: Optional[GuildModelOptions] = GuildModelOptions(),
    ):
        self.name = name
        self.default_maximum_member_count = default_maximum_member_count
        self.maximum_member_count = maximum_member_count
        self.inactivity_period_days = inactivity_period_days
        self.roles = roles
        self.guild_master_role = guild_master_role
        self.guild_member_default_role = guild_member_default_role
        self.rejoin_cool_time_minutes = rejoin_cool_time_minutes
        self.metadata = options.metadata if options.metadata else None
        self.max_concurrent_join_guilds = options.max_concurrent_join_guilds if options.max_concurrent_join_guilds else None
        self.max_concurrent_guild_master_count = options.max_concurrent_guild_master_count if options.max_concurrent_guild_master_count else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.default_maximum_member_count is not None:
            properties["defaultMaximumMemberCount"] = self.default_maximum_member_count
        if self.maximum_member_count is not None:
            properties["maximumMemberCount"] = self.maximum_member_count
        if self.inactivity_period_days is not None:
            properties["inactivityPeriodDays"] = self.inactivity_period_days
        if self.roles is not None:
            properties["roles"] = [
                v.properties(
                )
                for v in self.roles
            ]
        if self.guild_master_role is not None:
            properties["guildMasterRole"] = self.guild_master_role
        if self.guild_member_default_role is not None:
            properties["guildMemberDefaultRole"] = self.guild_member_default_role
        if self.rejoin_cool_time_minutes is not None:
            properties["rejoinCoolTimeMinutes"] = self.rejoin_cool_time_minutes
        if self.max_concurrent_join_guilds is not None:
            properties["maxConcurrentJoinGuilds"] = self.max_concurrent_join_guilds
        if self.max_concurrent_guild_master_count is not None:
            properties["maxConcurrentGuildMasterCount"] = self.max_concurrent_guild_master_count

        return properties
