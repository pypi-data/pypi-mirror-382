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
from .Contents import Contents
from ...core.model import VerifyAction
from ...core.model import ConsumeAction
from .options.QuestModelOptions import QuestModelOptions


class QuestModel:
    name: str
    contents: List[Contents]
    metadata: Optional[str] = None
    challenge_period_event_id: Optional[str] = None
    first_complete_acquire_actions: Optional[List[AcquireAction]] = None
    verify_actions: Optional[List[VerifyAction]] = None
    consume_actions: Optional[List[ConsumeAction]] = None
    failed_acquire_actions: Optional[List[AcquireAction]] = None
    premise_quest_names: Optional[List[str]] = None

    def __init__(
        self,
        name: str,
        contents: List[Contents],
        options: Optional[QuestModelOptions] = QuestModelOptions(),
    ):
        self.name = name
        self.contents = contents
        self.metadata = options.metadata if options.metadata else None
        self.challenge_period_event_id = options.challenge_period_event_id if options.challenge_period_event_id else None
        self.first_complete_acquire_actions = options.first_complete_acquire_actions if options.first_complete_acquire_actions else None
        self.verify_actions = options.verify_actions if options.verify_actions else None
        self.consume_actions = options.consume_actions if options.consume_actions else None
        self.failed_acquire_actions = options.failed_acquire_actions if options.failed_acquire_actions else None
        self.premise_quest_names = options.premise_quest_names if options.premise_quest_names else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.contents is not None:
            properties["contents"] = [
                v.properties(
                )
                for v in self.contents
            ]
        if self.challenge_period_event_id is not None:
            properties["challengePeriodEventId"] = self.challenge_period_event_id
        if self.first_complete_acquire_actions is not None:
            properties["firstCompleteAcquireActions"] = [
                v.properties(
                )
                for v in self.first_complete_acquire_actions
            ]
        if self.verify_actions is not None:
            properties["verifyActions"] = [
                v.properties(
                )
                for v in self.verify_actions
            ]
        if self.consume_actions is not None:
            properties["consumeActions"] = [
                v.properties(
                )
                for v in self.consume_actions
            ]
        if self.failed_acquire_actions is not None:
            properties["failedAcquireActions"] = [
                v.properties(
                )
                for v in self.failed_acquire_actions
            ]
        if self.premise_quest_names is not None:
            properties["premiseQuestNames"] = self.premise_quest_names

        return properties
