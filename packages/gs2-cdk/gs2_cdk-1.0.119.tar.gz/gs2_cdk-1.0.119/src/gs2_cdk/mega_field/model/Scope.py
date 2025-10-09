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
from .options.ScopeOptions import ScopeOptions


class Scope:
    layer_name: str
    r: float
    limit: int

    def __init__(
        self,
        layer_name: str,
        r: float,
        limit: int,
        options: Optional[ScopeOptions] = ScopeOptions(),
    ):
        self.layer_name = layer_name
        self.r = r
        self.limit = limit

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.layer_name is not None:
            properties["layerName"] = self.layer_name
        if self.r is not None:
            properties["r"] = self.r
        if self.limit is not None:
            properties["limit"] = self.limit

        return properties
