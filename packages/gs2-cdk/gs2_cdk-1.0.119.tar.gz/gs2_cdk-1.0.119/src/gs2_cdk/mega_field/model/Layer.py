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
from .options.LayerOptions import LayerOptions


class Layer:
    area_model_name: str
    layer_model_name: str
    number_of_min_entries: int
    number_of_max_entries: int
    height: int
    root: Optional[str] = None

    def __init__(
        self,
        area_model_name: str,
        layer_model_name: str,
        number_of_min_entries: int,
        number_of_max_entries: int,
        height: int,
        options: Optional[LayerOptions] = LayerOptions(),
    ):
        self.area_model_name = area_model_name
        self.layer_model_name = layer_model_name
        self.number_of_min_entries = number_of_min_entries
        self.number_of_max_entries = number_of_max_entries
        self.height = height
        self.root = options.root if options.root else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.area_model_name is not None:
            properties["areaModelName"] = self.area_model_name
        if self.layer_model_name is not None:
            properties["layerModelName"] = self.layer_model_name
        if self.root is not None:
            properties["root"] = self.root
        if self.number_of_min_entries is not None:
            properties["numberOfMinEntries"] = self.number_of_min_entries
        if self.number_of_max_entries is not None:
            properties["numberOfMaxEntries"] = self.number_of_max_entries
        if self.height is not None:
            properties["height"] = self.height

        return properties
