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
from .options.ItemModelOptions import ItemModelOptions


class ItemModel:
    name: str
    stacking_limit: int
    allow_multiple_stacks: bool
    sort_value: int
    metadata: Optional[str] = None

    def __init__(
        self,
        name: str,
        stacking_limit: int,
        allow_multiple_stacks: bool,
        sort_value: int,
        options: Optional[ItemModelOptions] = ItemModelOptions(),
    ):
        self.name = name
        self.stacking_limit = stacking_limit
        self.allow_multiple_stacks = allow_multiple_stacks
        self.sort_value = sort_value
        self.metadata = options.metadata if options.metadata else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.stacking_limit is not None:
            properties["stackingLimit"] = self.stacking_limit
        if self.allow_multiple_stacks is not None:
            properties["allowMultipleStacks"] = self.allow_multiple_stacks
        if self.sort_value is not None:
            properties["sortValue"] = self.sort_value

        return properties
