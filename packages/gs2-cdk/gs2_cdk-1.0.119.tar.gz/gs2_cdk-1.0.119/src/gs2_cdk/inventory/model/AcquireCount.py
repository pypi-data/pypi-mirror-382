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
from .options.AcquireCountOptions import AcquireCountOptions


class AcquireCount:
    item_name: str
    count: int

    def __init__(
        self,
        item_name: str,
        count: int,
        options: Optional[AcquireCountOptions] = AcquireCountOptions(),
    ):
        self.item_name = item_name
        self.count = count

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.item_name is not None:
            properties["itemName"] = self.item_name
        if self.count is not None:
            properties["count"] = self.count

        return properties
