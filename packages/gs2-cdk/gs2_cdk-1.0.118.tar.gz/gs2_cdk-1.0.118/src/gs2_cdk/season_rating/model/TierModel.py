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
from .options.TierModelOptions import TierModelOptions


class TierModel:
    raise_rank_bonus: int
    entry_fee: int
    minimum_change_point: int
    maximum_change_point: int
    metadata: Optional[str] = None

    def __init__(
        self,
        raise_rank_bonus: int,
        entry_fee: int,
        minimum_change_point: int,
        maximum_change_point: int,
        options: Optional[TierModelOptions] = TierModelOptions(),
    ):
        self.raise_rank_bonus = raise_rank_bonus
        self.entry_fee = entry_fee
        self.minimum_change_point = minimum_change_point
        self.maximum_change_point = maximum_change_point
        self.metadata = options.metadata if options.metadata else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.raise_rank_bonus is not None:
            properties["raiseRankBonus"] = self.raise_rank_bonus
        if self.entry_fee is not None:
            properties["entryFee"] = self.entry_fee
        if self.minimum_change_point is not None:
            properties["minimumChangePoint"] = self.minimum_change_point
        if self.maximum_change_point is not None:
            properties["maximumChangePoint"] = self.maximum_change_point

        return properties
