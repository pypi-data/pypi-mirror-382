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
from .options.CalculatedAtOptions import CalculatedAtOptions


class CalculatedAt:
    category_name: str
    calculated_at: int

    def __init__(
        self,
        category_name: str,
        calculated_at: int,
        options: Optional[CalculatedAtOptions] = CalculatedAtOptions(),
    ):
        self.category_name = category_name
        self.calculated_at = calculated_at

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.category_name is not None:
            properties["categoryName"] = self.category_name
        if self.calculated_at is not None:
            properties["calculatedAt"] = self.calculated_at

        return properties
