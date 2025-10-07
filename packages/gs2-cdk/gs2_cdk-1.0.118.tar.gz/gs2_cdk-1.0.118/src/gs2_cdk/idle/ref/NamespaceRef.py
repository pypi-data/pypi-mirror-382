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
from .CategoryModelRef import CategoryModelRef
from ..stamp_sheet.IncreaseMaximumIdleMinutesByUserId import IncreaseMaximumIdleMinutesByUserId
from ..stamp_sheet.SetMaximumIdleMinutesByUserId import SetMaximumIdleMinutesByUserId
from ..stamp_sheet.ReceiveByUserId import ReceiveByUserId
from ...core.model import Config
from ..stamp_sheet.DecreaseMaximumIdleMinutesByUserId import DecreaseMaximumIdleMinutesByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def category_model(
        self,
        category_name: str,
    ) -> CategoryModelRef:
        return CategoryModelRef(
            self.namespace_name,
            category_name,
        )

    def increase_maximum_idle_minutes(
        self,
        category_name: str,
        increase_minutes: Optional[int] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> IncreaseMaximumIdleMinutesByUserId:
        return IncreaseMaximumIdleMinutesByUserId(
            self.namespace_name,
            category_name,
            increase_minutes,
            user_id,
        )

    def set_maximum_idle_minutes(
        self,
        category_name: str,
        maximum_idle_minutes: Optional[int] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> SetMaximumIdleMinutesByUserId:
        return SetMaximumIdleMinutesByUserId(
            self.namespace_name,
            category_name,
            maximum_idle_minutes,
            user_id,
        )

    def receive(
        self,
        category_name: str,
        config: Optional[List[Config]] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> ReceiveByUserId:
        return ReceiveByUserId(
            self.namespace_name,
            category_name,
            config,
            user_id,
        )

    def decrease_maximum_idle_minutes(
        self,
        category_name: str,
        decrease_minutes: Optional[int] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> DecreaseMaximumIdleMinutesByUserId:
        return DecreaseMaximumIdleMinutesByUserId(
            self.namespace_name,
            category_name,
            decrease_minutes,
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
                "idle",
                self.namespace_name,
            ],
        ).str(
        )
