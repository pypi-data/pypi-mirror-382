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
from .options.MaterialOptions import MaterialOptions


class Material:
    material_item_set_id: str
    count: int

    def __init__(
        self,
        material_item_set_id: str,
        count: int,
        options: Optional[MaterialOptions] = MaterialOptions(),
    ):
        self.material_item_set_id = material_item_set_id
        self.count = count

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.material_item_set_id is not None:
            properties["materialItemSetId"] = self.material_item_set_id
        if self.count is not None:
            properties["count"] = self.count

        return properties
