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
from .Attribute import Attribute
from .options.PlayerOptions import PlayerOptions


class Player:
    user_id: str
    role_name: str
    attributes: Optional[List[Attribute]] = None
    deny_user_ids: Optional[List[str]] = None

    def __init__(
        self,
        user_id: str,
        role_name: str,
        options: Optional[PlayerOptions] = PlayerOptions(),
    ):
        self.user_id = user_id
        self.role_name = role_name
        self.attributes = options.attributes if options.attributes else None
        self.deny_user_ids = options.deny_user_ids if options.deny_user_ids else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.user_id is not None:
            properties["userId"] = self.user_id
        if self.attributes is not None:
            properties["attributes"] = [
                v.properties(
                )
                for v in self.attributes
            ]
        if self.role_name is not None:
            properties["roleName"] = self.role_name
        if self.deny_user_ids is not None:
            properties["denyUserIds"] = self.deny_user_ids

        return properties
