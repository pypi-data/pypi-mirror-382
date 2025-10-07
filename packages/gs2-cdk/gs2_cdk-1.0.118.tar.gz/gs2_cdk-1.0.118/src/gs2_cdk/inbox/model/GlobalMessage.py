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
from .TimeSpan import TimeSpan
from .options.GlobalMessageOptions import GlobalMessageOptions


class GlobalMessage:
    name: str
    metadata: str
    read_acquire_actions: Optional[List[AcquireAction]] = None
    expires_time_span: Optional[TimeSpan] = None
    expires_at: Optional[int] = None
    message_reception_period_event_id: Optional[str] = None

    def __init__(
        self,
        name: str,
        metadata: str,
        options: Optional[GlobalMessageOptions] = GlobalMessageOptions(),
    ):
        self.name = name
        self.metadata = metadata
        self.read_acquire_actions = options.read_acquire_actions if options.read_acquire_actions else None
        self.expires_time_span = options.expires_time_span if options.expires_time_span else None
        self.expires_at = options.expires_at if options.expires_at else None
        self.message_reception_period_event_id = options.message_reception_period_event_id if options.message_reception_period_event_id else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.read_acquire_actions is not None:
            properties["readAcquireActions"] = [
                v.properties(
                )
                for v in self.read_acquire_actions
            ]
        if self.expires_time_span is not None:
            properties["expiresTimeSpan"] = self.expires_time_span.properties(
            )
        if self.expires_at is not None:
            properties["expiresAt"] = self.expires_at
        if self.message_reception_period_event_id is not None:
            properties["messageReceptionPeriodEventId"] = self.message_reception_period_event_id

        return properties
