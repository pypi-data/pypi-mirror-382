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
from .ChangeStateEvent import ChangeStateEvent
from .EmitEvent import EmitEvent
from .options.EventOptions import EventOptions
from .options.EventEventTypeIsChangeStateOptions import EventEventTypeIsChangeStateOptions
from .options.EventEventTypeIsEmitOptions import EventEventTypeIsEmitOptions
from .enums.EventEventType import EventEventType


class Event:
    event_type: EventEventType
    change_state_event: Optional[ChangeStateEvent] = None
    emit_event: Optional[EmitEvent] = None

    def __init__(
        self,
        event_type: EventEventType,
        options: Optional[EventOptions] = EventOptions(),
    ):
        self.event_type = event_type
        self.change_state_event = options.change_state_event if options.change_state_event else None
        self.emit_event = options.emit_event if options.emit_event else None

    @staticmethod
    def event_type_is_change_state(
        change_state_event: ChangeStateEvent,
        options: Optional[EventEventTypeIsChangeStateOptions] = EventEventTypeIsChangeStateOptions(),
    ) -> Event:
        return Event(
            EventEventType.CHANGE_STATE,
            EventOptions(
                change_state_event,
            ),
        )

    @staticmethod
    def event_type_is_emit(
        emit_event: EmitEvent,
        options: Optional[EventEventTypeIsEmitOptions] = EventEventTypeIsEmitOptions(),
    ) -> Event:
        return Event(
            EventEventType.EMIT,
            EventOptions(
                emit_event,
            ),
        )

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.event_type is not None:
            properties["eventType"] = self.event_type.value
        if self.change_state_event is not None:
            properties["changeStateEvent"] = self.change_state_event.properties(
            )
        if self.emit_event is not None:
            properties["emitEvent"] = self.emit_event.properties(
            )

        return properties
