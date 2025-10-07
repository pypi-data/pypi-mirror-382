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
from .options.PrizeLimitOptions import PrizeLimitOptions


class PrizeLimit:
    prize_id: str
    drawn_count: int
    revision: Optional[int] = None

    def __init__(
        self,
        prize_id: str,
        drawn_count: int,
        options: Optional[PrizeLimitOptions] = PrizeLimitOptions(),
    ):
        self.prize_id = prize_id
        self.drawn_count = drawn_count
        self.revision = options.revision if options.revision else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.prize_id is not None:
            properties["prizeId"] = self.prize_id
        if self.drawn_count is not None:
            properties["drawnCount"] = self.drawn_count

        return properties
