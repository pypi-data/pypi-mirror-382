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
from .BonusRate import BonusRate
from .options.RateModelOptions import RateModelOptions


class RateModel:
    name: str
    target_inventory_model_id: str
    acquire_experience_suffix: str
    material_inventory_model_id: str
    experience_model_id: str
    description: Optional[str] = None
    metadata: Optional[str] = None
    acquire_experience_hierarchy: Optional[List[str]] = None
    bonus_rates: Optional[List[BonusRate]] = None

    def __init__(
        self,
        name: str,
        target_inventory_model_id: str,
        acquire_experience_suffix: str,
        material_inventory_model_id: str,
        experience_model_id: str,
        options: Optional[RateModelOptions] = RateModelOptions(),
    ):
        self.name = name
        self.target_inventory_model_id = target_inventory_model_id
        self.acquire_experience_suffix = acquire_experience_suffix
        self.material_inventory_model_id = material_inventory_model_id
        self.experience_model_id = experience_model_id
        self.description = options.description if options.description else None
        self.metadata = options.metadata if options.metadata else None
        self.acquire_experience_hierarchy = options.acquire_experience_hierarchy if options.acquire_experience_hierarchy else None
        self.bonus_rates = options.bonus_rates if options.bonus_rates else None

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
        if self.acquire_experience_suffix is not None:
            properties["acquireExperienceSuffix"] = self.acquire_experience_suffix
        if self.material_inventory_model_id is not None:
            properties["materialInventoryModelId"] = self.material_inventory_model_id
        if self.acquire_experience_hierarchy is not None:
            properties["acquireExperienceHierarchy"] = self.acquire_experience_hierarchy
        if self.experience_model_id is not None:
            properties["experienceModelId"] = self.experience_model_id
        if self.bonus_rates is not None:
            properties["bonusRates"] = [
                v.properties(
                )
                for v in self.bonus_rates
            ]

        return properties
