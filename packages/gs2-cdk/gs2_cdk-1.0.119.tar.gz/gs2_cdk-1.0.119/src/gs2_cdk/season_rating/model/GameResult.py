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
from .options.GameResultOptions import GameResultOptions


class GameResult:
    rank: int
    user_id: str

    def __init__(
        self,
        rank: int,
        user_id: str,
        options: Optional[GameResultOptions] = GameResultOptions(),
    ):
        self.rank = rank
        self.user_id = user_id

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.rank is not None:
            properties["rank"] = self.rank
        if self.user_id is not None:
            properties["userId"] = self.user_id

        return properties
