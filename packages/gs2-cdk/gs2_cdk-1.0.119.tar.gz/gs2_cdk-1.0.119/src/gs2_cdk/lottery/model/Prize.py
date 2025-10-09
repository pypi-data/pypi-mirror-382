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
from .options.PrizeOptions import PrizeOptions
from .options.PrizeTypeIsActionOptions import PrizeTypeIsActionOptions
from .options.PrizeTypeIsPrizeTableOptions import PrizeTypeIsPrizeTableOptions
from .enums.PrizeType import PrizeType


class Prize:
    prize_id: str
    type: PrizeType
    weight: int
    acquire_actions: Optional[List[AcquireAction]] = None
    drawn_limit: Optional[int] = None
    limit_fail_over_prize_id: Optional[str] = None
    prize_table_name: Optional[str] = None

    def __init__(
        self,
        prize_id: str,
        type: PrizeType,
        weight: int,
        options: Optional[PrizeOptions] = PrizeOptions(),
    ):
        self.prize_id = prize_id
        self.type = type
        self.weight = weight
        self.acquire_actions = options.acquire_actions if options.acquire_actions else None
        self.drawn_limit = options.drawn_limit if options.drawn_limit else None
        self.limit_fail_over_prize_id = options.limit_fail_over_prize_id if options.limit_fail_over_prize_id else None
        self.prize_table_name = options.prize_table_name if options.prize_table_name else None

    @staticmethod
    def type_is_action(
        prize_id: str,
        weight: int,
        acquire_actions: List[AcquireAction],
        options: Optional[PrizeTypeIsActionOptions] = PrizeTypeIsActionOptions(),
    ) -> Prize:
        return Prize(
            prize_id,
            PrizeType.ACTION,
            weight,
            PrizeOptions(
                acquire_actions,
                options.drawn_limit,
            ),
        )

    @staticmethod
    def type_is_prize_table(
        prize_id: str,
        weight: int,
        prize_table_name: str,
        options: Optional[PrizeTypeIsPrizeTableOptions] = PrizeTypeIsPrizeTableOptions(),
    ) -> Prize:
        return Prize(
            prize_id,
            PrizeType.PRIZE_TABLE,
            weight,
            PrizeOptions(
                prize_table_name,
                options.drawn_limit,
            ),
        )

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.prize_id is not None:
            properties["prizeId"] = self.prize_id
        if self.type is not None:
            properties["type"] = self.type.value
        if self.acquire_actions is not None:
            properties["acquireActions"] = [
                v.properties(
                )
                for v in self.acquire_actions
            ]
        if self.drawn_limit is not None:
            properties["drawnLimit"] = self.drawn_limit
        if self.limit_fail_over_prize_id is not None:
            properties["limitFailOverPrizeId"] = self.limit_fail_over_prize_id
        if self.prize_table_name is not None:
            properties["prizeTableName"] = self.prize_table_name
        if self.weight is not None:
            properties["weight"] = self.weight

        return properties
