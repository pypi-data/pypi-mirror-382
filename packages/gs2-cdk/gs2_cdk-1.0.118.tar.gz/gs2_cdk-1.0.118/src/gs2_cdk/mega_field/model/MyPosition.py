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
from .Position import Position
from .Vector import Vector
from .options.MyPositionOptions import MyPositionOptions


class MyPosition:
    position: Position
    vector: Vector
    r: float

    def __init__(
        self,
        position: Position,
        vector: Vector,
        r: float,
        options: Optional[MyPositionOptions] = MyPositionOptions(),
    ):
        self.position = position
        self.vector = vector
        self.r = r

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.position is not None:
            properties["position"] = self.position.properties(
            )
        if self.vector is not None:
            properties["vector"] = self.vector.properties(
            )
        if self.r is not None:
            properties["r"] = self.r

        return properties
