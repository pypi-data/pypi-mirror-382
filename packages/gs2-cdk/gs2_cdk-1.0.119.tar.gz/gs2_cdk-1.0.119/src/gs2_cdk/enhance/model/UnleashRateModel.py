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
from .UnleashRateEntryModel import UnleashRateEntryModel
from .options.UnleashRateModelOptions import UnleashRateModelOptions


class UnleashRateModel:
    name: str
    target_inventory_model_id: str
    grade_model_id: str
    grade_entries: List[UnleashRateEntryModel]
    description: Optional[str] = None
    metadata: Optional[str] = None

    def __init__(
        self,
        name: str,
        target_inventory_model_id: str,
        grade_model_id: str,
        grade_entries: List[UnleashRateEntryModel],
        options: Optional[UnleashRateModelOptions] = UnleashRateModelOptions(),
    ):
        self.name = name
        self.target_inventory_model_id = target_inventory_model_id
        self.grade_model_id = grade_model_id
        self.grade_entries = grade_entries
        self.description = options.description if options.description else None
        self.metadata = options.metadata if options.metadata else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.description is not None:
            properties["description"] = self.description
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.target_inventory_model_id is not None:
            properties["targetInventoryModelId"] = self.target_inventory_model_id
        if self.grade_model_id is not None:
            properties["gradeModelId"] = self.grade_model_id
        if self.grade_entries is not None:
            properties["gradeEntries"] = [
                v.properties(
                )
                for v in self.grade_entries
            ]

        return properties
