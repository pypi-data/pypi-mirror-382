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
from .options.RarityParameterCountModelOptions import RarityParameterCountModelOptions


class RarityParameterCountModel:
    count: int
    weight: int

    def __init__(
        self,
        count: int,
        weight: int,
        options: Optional[RarityParameterCountModelOptions] = RarityParameterCountModelOptions(),
    ):
        self.count = count
        self.weight = weight

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.count is not None:
            properties["count"] = self.count
        if self.weight is not None:
            properties["weight"] = self.weight

        return properties
