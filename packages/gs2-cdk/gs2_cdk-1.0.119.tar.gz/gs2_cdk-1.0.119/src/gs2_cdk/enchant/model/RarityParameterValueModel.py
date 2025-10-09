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
from .options.RarityParameterValueModelOptions import RarityParameterValueModelOptions


class RarityParameterValueModel:
    name: str
    resource_name: str
    resource_value: int
    weight: int
    metadata: Optional[str] = None

    def __init__(
        self,
        name: str,
        resource_name: str,
        resource_value: int,
        weight: int,
        options: Optional[RarityParameterValueModelOptions] = RarityParameterValueModelOptions(),
    ):
        self.name = name
        self.resource_name = resource_name
        self.resource_value = resource_value
        self.weight = weight
        self.metadata = options.metadata if options.metadata else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.resource_name is not None:
            properties["resourceName"] = self.resource_name
        if self.resource_value is not None:
            properties["resourceValue"] = self.resource_value
        if self.weight is not None:
            properties["weight"] = self.weight

        return properties
