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
from .IgnoreUser import IgnoreUser
from .options.IgnoreUsersOptions import IgnoreUsersOptions


class IgnoreUsers:
    guild_model_name: str
    users: Optional[List[IgnoreUser]] = None
    revision: Optional[int] = None

    def __init__(
        self,
        guild_model_name: str,
        options: Optional[IgnoreUsersOptions] = IgnoreUsersOptions(),
    ):
        self.guild_model_name = guild_model_name
        self.users = options.users if options.users else None
        self.revision = options.revision if options.revision else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.guild_model_name is not None:
            properties["guildModelName"] = self.guild_model_name
        if self.users is not None:
            properties["users"] = [
                v.properties(
                )
                for v in self.users
            ]

        return properties
