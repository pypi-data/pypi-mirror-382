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

from ...core.model import CdkResource, Stack
from ...core.func import GetAttr

from ..ref.StageRef import StageRef
from .enums.StageStatus import StageStatus

from .options.StageOptions import StageOptions


class Stage(CdkResource):
    stack: Stack
    owner_id: str
    name: str
    sort_number: int
    source_stage_name: Optional[str] = None

    def __init__(
        self,
        stack: Stack,
        owner_id: str,
        name: str,
        sort_number: int,
        options: Optional[StageOptions] = StageOptions(),
    ):
        super().__init__(
            "Freeze_Stage_" + name
        )

        self.stack = stack
        self.owner_id = owner_id
        self.name = name
        self.sort_number = sort_number
        self.source_stage_name = options.source_stage_name if options.source_stage_name else None
        stack.add_resource(
            self,
        )


    def alternate_keys(
        self,
    ):
        return "name"

    def resource_type(
        self,
    ) -> str:
        return "GS2::Freeze::Stage"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.owner_id is not None:
            properties["OwnerId"] = self.owner_id
        if self.name is not None:
            properties["Name"] = self.name
        if self.source_stage_name is not None:
            properties["SourceStageName"] = self.source_stage_name
        if self.sort_number is not None:
            properties["SortNumber"] = self.sort_number

        return properties

    def ref(
        self,
    ) -> StageRef:
        return StageRef(
            self.name,
        )

    def get_attr_stage_id(
        self,
    ) -> GetAttr:
        return GetAttr(
            self,
            "Item.StageId",
            None,
        )
