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
from .Threshold import Threshold
from .AcquireActionRate import AcquireActionRate
from .options.ExperienceModelOptions import ExperienceModelOptions


class ExperienceModel:
    name: str
    default_experience: int
    default_rank_cap: int
    max_rank_cap: int
    rank_threshold: Threshold
    metadata: Optional[str] = None
    acquire_action_rates: Optional[List[AcquireActionRate]] = None

    def __init__(
        self,
        name: str,
        default_experience: int,
        default_rank_cap: int,
        max_rank_cap: int,
        rank_threshold: Threshold,
        options: Optional[ExperienceModelOptions] = ExperienceModelOptions(),
    ):
        self.name = name
        self.default_experience = default_experience
        self.default_rank_cap = default_rank_cap
        self.max_rank_cap = max_rank_cap
        self.rank_threshold = rank_threshold
        self.metadata = options.metadata if options.metadata else None
        self.acquire_action_rates = options.acquire_action_rates if options.acquire_action_rates else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.default_experience is not None:
            properties["defaultExperience"] = self.default_experience
        if self.default_rank_cap is not None:
            properties["defaultRankCap"] = self.default_rank_cap
        if self.max_rank_cap is not None:
            properties["maxRankCap"] = self.max_rank_cap
        if self.rank_threshold is not None:
            properties["rankThreshold"] = self.rank_threshold.properties(
            )
        if self.acquire_action_rates is not None:
            properties["acquireActionRates"] = [
                v.properties(
                )
                for v in self.acquire_action_rates
            ]

        return properties
