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
from ...core.model import AcquireAction
from .options.ContentsOptions import ContentsOptions


class Contents:
    weight: int
    metadata: Optional[str] = None
    complete_acquire_actions: Optional[List[AcquireAction]] = None

    def __init__(
        self,
        weight: int,
        options: Optional[ContentsOptions] = ContentsOptions(),
    ):
        self.weight = weight
        self.metadata = options.metadata if options.metadata else None
        self.complete_acquire_actions = options.complete_acquire_actions if options.complete_acquire_actions else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.complete_acquire_actions is not None:
            properties["completeAcquireActions"] = [
                v.properties(
                )
                for v in self.complete_acquire_actions
            ]
        if self.weight is not None:
            properties["weight"] = self.weight

        return properties
