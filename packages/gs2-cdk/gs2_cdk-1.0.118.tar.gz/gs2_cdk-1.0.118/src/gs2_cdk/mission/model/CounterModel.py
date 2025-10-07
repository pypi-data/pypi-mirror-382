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
from ...core.model import VerifyAction
from .CounterScopeModel import CounterScopeModel
from .options.CounterModelOptions import CounterModelOptions


class CounterModel:
    name: str
    scopes: List[CounterScopeModel]
    metadata: Optional[str] = None
    challenge_period_event_id: Optional[str] = None

    def __init__(
        self,
        name: str,
        scopes: List[CounterScopeModel],
        options: Optional[CounterModelOptions] = CounterModelOptions(),
    ):
        self.name = name
        self.scopes = scopes
        self.metadata = options.metadata if options.metadata else None
        self.challenge_period_event_id = options.challenge_period_event_id if options.challenge_period_event_id else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.scopes is not None:
            properties["scopes"] = [
                v.properties(
                )
                for v in self.scopes
            ]
        if self.challenge_period_event_id is not None:
            properties["challengePeriodEventId"] = self.challenge_period_event_id

        return properties
