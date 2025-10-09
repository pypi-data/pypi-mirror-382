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
from .options.PositionOptions import PositionOptions


class Position:
    x: float
    y: float
    z: float

    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        options: Optional[PositionOptions] = PositionOptions(),
    ):
        self.x = x
        self.y = y
        self.z = z

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.x is not None:
            properties["x"] = self.x
        if self.y is not None:
            properties["y"] = self.y
        if self.z is not None:
            properties["z"] = self.z

        return properties
