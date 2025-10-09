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
from .Player import Player
from .options.CapacityOfRoleOptions import CapacityOfRoleOptions


class CapacityOfRole:
    role_name: str
    capacity: int
    role_aliases: Optional[List[str]] = None
    participants: Optional[List[Player]] = None

    def __init__(
        self,
        role_name: str,
        capacity: int,
        options: Optional[CapacityOfRoleOptions] = CapacityOfRoleOptions(),
    ):
        self.role_name = role_name
        self.capacity = capacity
        self.role_aliases = options.role_aliases if options.role_aliases else None
        self.participants = options.participants if options.participants else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.role_name is not None:
            properties["roleName"] = self.role_name
        if self.role_aliases is not None:
            properties["roleAliases"] = self.role_aliases
        if self.capacity is not None:
            properties["capacity"] = self.capacity
        if self.participants is not None:
            properties["participants"] = [
                v.properties(
                )
                for v in self.participants
            ]

        return properties
