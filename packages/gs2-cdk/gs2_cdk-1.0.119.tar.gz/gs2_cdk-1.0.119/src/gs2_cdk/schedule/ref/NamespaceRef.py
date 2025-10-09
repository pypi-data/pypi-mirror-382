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
from ..stamp_sheet.TriggerByUserId import TriggerByUserId
from ..stamp_sheet.ExtendTriggerByUserId import ExtendTriggerByUserId
from ..stamp_sheet.DeleteTriggerByUserId import DeleteTriggerByUserId
from ..stamp_sheet.VerifyTriggerByUserId import VerifyTriggerByUserId
from ..stamp_sheet.VerifyEventByUserId import VerifyEventByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def trigger(
        self,
        trigger_name: str,
        trigger_strategy: str,
        ttl: Optional[int] = None,
        event_id: Optional[str] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> TriggerByUserId:
        return TriggerByUserId(
            self.namespace_name,
            trigger_name,
            trigger_strategy,
            ttl,
            event_id,
            user_id,
        )

    def extend_trigger(
        self,
        trigger_name: str,
        extend_seconds: int,
        user_id: Optional[str] = "#{userId}",
    ) -> ExtendTriggerByUserId:
        return ExtendTriggerByUserId(
            self.namespace_name,
            trigger_name,
            extend_seconds,
            user_id,
        )

    def delete_trigger(
        self,
        trigger_name: str,
        user_id: Optional[str] = "#{userId}",
    ) -> DeleteTriggerByUserId:
        return DeleteTriggerByUserId(
            self.namespace_name,
            trigger_name,
            user_id,
        )

    def verify_trigger(
        self,
        trigger_name: str,
        verify_type: str,
        elapsed_minutes: Optional[int] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyTriggerByUserId:
        return VerifyTriggerByUserId(
            self.namespace_name,
            trigger_name,
            verify_type,
            elapsed_minutes,
            user_id,
        )

    def verify_event(
        self,
        event_name: str,
        verify_type: str,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyEventByUserId:
        return VerifyEventByUserId(
            self.namespace_name,
            event_name,
            verify_type,
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
                "schedule",
                self.namespace_name,
            ],
        ).str(
        )
