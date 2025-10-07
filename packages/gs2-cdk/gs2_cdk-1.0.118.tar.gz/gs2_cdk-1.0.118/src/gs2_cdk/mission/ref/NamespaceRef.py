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

from ...core.func import GetAttr, Join
from .MissionGroupModelRef import MissionGroupModelRef
from .CounterModelRef import CounterModelRef
from ..stamp_sheet.RevertReceiveByUserId import RevertReceiveByUserId
from ..stamp_sheet.IncreaseCounterByUserId import IncreaseCounterByUserId
from ..stamp_sheet.SetCounterByUserId import SetCounterByUserId
from ..model.ScopedValue import ScopedValue
from ..stamp_sheet.ReceiveByUserId import ReceiveByUserId
from ..stamp_sheet.BatchReceiveByUserId import BatchReceiveByUserId
from ..stamp_sheet.DecreaseCounterByUserId import DecreaseCounterByUserId
from ..stamp_sheet.ResetCounterByUserId import ResetCounterByUserId
from ..stamp_sheet.VerifyCompleteByUserId import VerifyCompleteByUserId
from ..stamp_sheet.VerifyCounterValueByUserId import VerifyCounterValueByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def mission_group_model(
        self,
        mission_group_name: str,
    ) -> MissionGroupModelRef:
        return MissionGroupModelRef(
            self.namespace_name,
            mission_group_name,
        )

    def counter_model(
        self,
        counter_name: str,
    ) -> CounterModelRef:
        return CounterModelRef(
            self.namespace_name,
            counter_name,
        )

    def revert_receive(
        self,
        mission_group_name: str,
        mission_task_name: str,
        user_id: Optional[str] = "#{userId}",
    ) -> RevertReceiveByUserId:
        return RevertReceiveByUserId(
            self.namespace_name,
            mission_group_name,
            mission_task_name,
            user_id,
        )

    def increase_counter(
        self,
        counter_name: str,
        value: int,
        user_id: Optional[str] = "#{userId}",
    ) -> IncreaseCounterByUserId:
        return IncreaseCounterByUserId(
            self.namespace_name,
            counter_name,
            value,
            user_id,
        )

    def set_counter(
        self,
        counter_name: str,
        values: Optional[List[ScopedValue]] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> SetCounterByUserId:
        return SetCounterByUserId(
            self.namespace_name,
            counter_name,
            values,
            user_id,
        )

    def receive(
        self,
        mission_group_name: str,
        mission_task_name: str,
        user_id: Optional[str] = "#{userId}",
    ) -> ReceiveByUserId:
        return ReceiveByUserId(
            self.namespace_name,
            mission_group_name,
            mission_task_name,
            user_id,
        )

    def batch_receive(
        self,
        mission_group_name: str,
        mission_task_names: List[str],
        user_id: Optional[str] = "#{userId}",
    ) -> BatchReceiveByUserId:
        return BatchReceiveByUserId(
            self.namespace_name,
            mission_group_name,
            mission_task_names,
            user_id,
        )

    def decrease_counter(
        self,
        counter_name: str,
        value: int,
        user_id: Optional[str] = "#{userId}",
    ) -> DecreaseCounterByUserId:
        return DecreaseCounterByUserId(
            self.namespace_name,
            counter_name,
            value,
            user_id,
        )

    def reset_counter(
        self,
        counter_name: str,
        scopes: List[ScopedValue],
        user_id: Optional[str] = "#{userId}",
    ) -> ResetCounterByUserId:
        return ResetCounterByUserId(
            self.namespace_name,
            counter_name,
            scopes,
            user_id,
        )

    def verify_complete(
        self,
        mission_group_name: str,
        verify_type: str,
        mission_task_name: str,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyCompleteByUserId:
        return VerifyCompleteByUserId(
            self.namespace_name,
            mission_group_name,
            verify_type,
            mission_task_name,
            multiply_value_specifying_quantity,
            user_id,
        )

    def verify_counter_value(
        self,
        counter_name: str,
        verify_type: str,
        scope_type: Optional[str] = None,
        reset_type: Optional[str] = None,
        condition_name: Optional[str] = None,
        value: Optional[int] = None,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyCounterValueByUserId:
        return VerifyCounterValueByUserId(
            self.namespace_name,
            counter_name,
            verify_type,
            scope_type,
            reset_type,
            condition_name,
            value,
            multiply_value_specifying_quantity,
            user_id,
        )

    def grn(
        self,
    ) -> str:
        return Join(
            ":",
            [
                "grn",
                "gs2",
                GetAttr.region(
                ).str(
                ),
                GetAttr.owner_id(
                ).str(
                ),
                "mission",
                self.namespace_name,
            ],
        ).str(
        )
