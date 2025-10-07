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
from .BonusModelRef import BonusModelRef
from ..stamp_sheet.DeleteReceiveStatusByUserId import DeleteReceiveStatusByUserId
from ..stamp_sheet.UnmarkReceivedByUserId import UnmarkReceivedByUserId
from ..stamp_sheet.MarkReceivedByUserId import MarkReceivedByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def bonus_model(
        self,
        bonus_model_name: str,
    ) -> BonusModelRef:
        return BonusModelRef(
            self.namespace_name,
            bonus_model_name,
        )

    def delete_receive_status(
        self,
        bonus_model_name: str,
        user_id: Optional[str] = "#{userId}",
    ) -> DeleteReceiveStatusByUserId:
        return DeleteReceiveStatusByUserId(
            self.namespace_name,
            bonus_model_name,
            user_id,
        )

    def unmark_received(
        self,
        bonus_model_name: str,
        step_number: int,
        user_id: Optional[str] = "#{userId}",
    ) -> UnmarkReceivedByUserId:
        return UnmarkReceivedByUserId(
            self.namespace_name,
            bonus_model_name,
            step_number,
            user_id,
        )

    def mark_received(
        self,
        bonus_model_name: str,
        step_number: int,
        user_id: Optional[str] = "#{userId}",
    ) -> MarkReceivedByUserId:
        return MarkReceivedByUserId(
            self.namespace_name,
            bonus_model_name,
            step_number,
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
                "loginReward",
                self.namespace_name,
            ],
        ).str(
        )
