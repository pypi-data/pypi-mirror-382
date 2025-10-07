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
from .options.SeasonModelOptions import SeasonModelOptions


class SeasonModel:
    name: str
    maximum_participants: int
    challenge_period_event_id: str
    metadata: Optional[str] = None
    experience_model_id: Optional[str] = None

    def __init__(
        self,
        name: str,
        maximum_participants: int,
        challenge_period_event_id: str,
        options: Optional[SeasonModelOptions] = SeasonModelOptions(),
    ):
        self.name = name
        self.maximum_participants = maximum_participants
        self.challenge_period_event_id = challenge_period_event_id
        self.metadata = options.metadata if options.metadata else None
        self.experience_model_id = options.experience_model_id if options.experience_model_id else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.maximum_participants is not None:
            properties["maximumParticipants"] = self.maximum_participants
        if self.experience_model_id is not None:
            properties["experienceModelId"] = self.experience_model_id
        if self.challenge_period_event_id is not None:
            properties["challengePeriodEventId"] = self.challenge_period_event_id

        return properties
