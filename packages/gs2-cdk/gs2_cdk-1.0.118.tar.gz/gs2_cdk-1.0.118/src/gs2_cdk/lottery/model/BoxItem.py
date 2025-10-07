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
from .options.BoxItemOptions import BoxItemOptions


class BoxItem:
    prize_id: str
    remaining: int
    initial: int
    acquire_actions: Optional[List[AcquireAction]] = None

    def __init__(
        self,
        prize_id: str,
        remaining: int,
        initial: int,
        options: Optional[BoxItemOptions] = BoxItemOptions(),
    ):
        self.prize_id = prize_id
        self.remaining = remaining
        self.initial = initial
        self.acquire_actions = options.acquire_actions if options.acquire_actions else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.prize_id is not None:
            properties["prizeId"] = self.prize_id
        if self.acquire_actions is not None:
            properties["acquireActions"] = [
                v.properties(
                )
                for v in self.acquire_actions
            ]
        if self.remaining is not None:
            properties["remaining"] = self.remaining
        if self.initial is not None:
            properties["initial"] = self.initial

        return properties
