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
from .ItemModel import ItemModel
from .options.InventoryModelOptions import InventoryModelOptions


class InventoryModel:
    name: str
    initial_capacity: int
    max_capacity: int
    item_models: List[ItemModel]
    metadata: Optional[str] = None
    protect_referenced_item: Optional[bool] = None

    def __init__(
        self,
        name: str,
        initial_capacity: int,
        max_capacity: int,
        item_models: List[ItemModel],
        options: Optional[InventoryModelOptions] = InventoryModelOptions(),
    ):
        self.name = name
        self.initial_capacity = initial_capacity
        self.max_capacity = max_capacity
        self.item_models = item_models
        self.metadata = options.metadata if options.metadata else None
        self.protect_referenced_item = options.protect_referenced_item if options.protect_referenced_item else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.initial_capacity is not None:
            properties["initialCapacity"] = self.initial_capacity
        if self.max_capacity is not None:
            properties["maxCapacity"] = self.max_capacity
        if self.protect_referenced_item is not None:
            properties["protectReferencedItem"] = self.protect_referenced_item
        if self.item_models is not None:
            properties["itemModels"] = [
                v.properties(
                )
                for v in self.item_models
            ]

        return properties
