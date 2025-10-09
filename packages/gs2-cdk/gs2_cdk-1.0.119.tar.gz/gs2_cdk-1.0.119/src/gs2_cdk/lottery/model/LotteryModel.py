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
#
# deny overwrite
from __future__ import annotations
from typing import *
from .options.LotteryModelOptions import LotteryModelOptions
from .options.LotteryModelMethodIsPrizeTableOptions import LotteryModelMethodIsPrizeTableOptions
from .options.LotteryModelMethodIsScriptOptions import LotteryModelMethodIsScriptOptions
from .enums.LotteryModelMode import LotteryModelMode
from .enums.LotteryModelMethod import LotteryModelMethod


class LotteryModel:
    name: str
    mode: LotteryModelMode
    method: LotteryModelMethod
    metadata: Optional[str] = None
    prize_table_name: Optional[str] = None
    choice_prize_table_script_id: Optional[str] = None

    def __init__(
        self,
        name: str,
        mode: LotteryModelMode,
        method: LotteryModelMethod,
        options: Optional[LotteryModelOptions] = LotteryModelOptions(),
    ):
        self.name = name
        self.mode = mode
        self.method = method
        self.metadata = options.metadata if options.metadata else None
        self.prize_table_name = options.prize_table_name if options.prize_table_name else None
        self.choice_prize_table_script_id = options.choice_prize_table_script_id if options.choice_prize_table_script_id else None

    @staticmethod
    def method_is_prize_table(
        name: str,
        mode: LotteryModelMode,
        options: Optional[LotteryModelMethodIsPrizeTableOptions] = LotteryModelMethodIsPrizeTableOptions(),
    ) -> LotteryModel:
        return LotteryModel(
            name,
            mode,
            LotteryModelMethod.PRIZE_TABLE,
            LotteryModelOptions(
                options.metadata,
                options.prize_table_name,
            ),
        )

    @staticmethod
    def method_is_script(
        name: str,
        mode: LotteryModelMode,
        options: Optional[LotteryModelMethodIsScriptOptions] = LotteryModelMethodIsScriptOptions(),
    ) -> LotteryModel:
        return LotteryModel(
            name,
            mode,
            LotteryModelMethod.SCRIPT,
            LotteryModelOptions(
                options.metadata,
            ),
        )

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.mode is not None:
            properties["mode"] = self.mode.value
        if self.method is not None:
            properties["method"] = self.method.value
        if self.prize_table_name is not None:
            properties["prizeTableName"] = self.prize_table_name
        if self.choice_prize_table_script_id is not None:
            properties["choicePrizeTableScriptId"] = self.choice_prize_table_script_id

        return properties
