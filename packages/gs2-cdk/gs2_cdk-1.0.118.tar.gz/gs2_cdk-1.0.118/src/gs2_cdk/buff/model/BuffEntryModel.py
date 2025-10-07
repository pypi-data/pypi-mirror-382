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
from .BuffTargetGrn import BuffTargetGrn
from .BuffTargetModel import BuffTargetModel
from .BuffTargetAction import BuffTargetAction
from .options.BuffEntryModelOptions import BuffEntryModelOptions
from .options.BuffEntryModelTargetTypeIsModelOptions import BuffEntryModelTargetTypeIsModelOptions
from .options.BuffEntryModelTargetTypeIsActionOptions import BuffEntryModelTargetTypeIsActionOptions
from .enums.BuffEntryModelExpression import BuffEntryModelExpression
from .enums.BuffEntryModelTargetType import BuffEntryModelTargetType


class BuffEntryModel:
    name: str
    expression: BuffEntryModelExpression
    target_type: BuffEntryModelTargetType
    priority: int
    metadata: Optional[str] = None
    target_model: Optional[BuffTargetModel] = None
    target_action: Optional[BuffTargetAction] = None
    apply_period_schedule_event_id: Optional[str] = None

    def __init__(
        self,
        name: str,
        expression: BuffEntryModelExpression,
        target_type: BuffEntryModelTargetType,
        priority: int,
        options: Optional[BuffEntryModelOptions] = BuffEntryModelOptions(),
    ):
        self.name = name
        self.expression = expression
        self.target_type = target_type
        self.priority = priority
        self.metadata = options.metadata if options.metadata else None
        self.target_model = options.target_model if options.target_model else None
        self.target_action = options.target_action if options.target_action else None
        self.apply_period_schedule_event_id = options.apply_period_schedule_event_id if options.apply_period_schedule_event_id else None

    @staticmethod
    def target_type_is_model(
        name: str,
        expression: BuffEntryModelExpression,
        priority: int,
        target_model: BuffTargetModel,
        options: Optional[BuffEntryModelTargetTypeIsModelOptions] = BuffEntryModelTargetTypeIsModelOptions(),
    ) -> BuffEntryModel:
        return BuffEntryModel(
            name,
            expression,
            BuffEntryModelTargetType.MODEL,
            priority,
            BuffEntryModelOptions(
                target_model,
                options.metadata,
                options.apply_period_schedule_event_id,
            ),
        )

    @staticmethod
    def target_type_is_action(
        name: str,
        expression: BuffEntryModelExpression,
        priority: int,
        target_action: BuffTargetAction,
        options: Optional[BuffEntryModelTargetTypeIsActionOptions] = BuffEntryModelTargetTypeIsActionOptions(),
    ) -> BuffEntryModel:
        return BuffEntryModel(
            name,
            expression,
            BuffEntryModelTargetType.ACTION,
            priority,
            BuffEntryModelOptions(
                target_action,
                options.metadata,
                options.apply_period_schedule_event_id,
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
        if self.expression is not None:
            properties["expression"] = self.expression.value
        if self.target_type is not None:
            properties["targetType"] = self.target_type.value
        if self.target_model is not None:
            properties["targetModel"] = self.target_model.properties(
            )
        if self.target_action is not None:
            properties["targetAction"] = self.target_action.properties(
            )
        if self.priority is not None:
            properties["priority"] = self.priority
        if self.apply_period_schedule_event_id is not None:
            properties["applyPeriodScheduleEventId"] = self.apply_period_schedule_event_id

        return properties
