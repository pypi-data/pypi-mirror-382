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
from .options.RankingRewardOptions import RankingRewardOptions


class RankingReward:
    threshold_rank: int
    metadata: Optional[str] = None
    acquire_actions: Optional[List[AcquireAction]] = None

    def __init__(
        self,
        threshold_rank: int,
        options: Optional[RankingRewardOptions] = RankingRewardOptions(),
    ):
        self.threshold_rank = threshold_rank
        self.metadata = options.metadata if options.metadata else None
        self.acquire_actions = options.acquire_actions if options.acquire_actions else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.threshold_rank is not None:
            properties["thresholdRank"] = self.threshold_rank
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.acquire_actions is not None:
            properties["acquireActions"] = [
                v.properties(
                )
                for v in self.acquire_actions
            ]

        return properties
