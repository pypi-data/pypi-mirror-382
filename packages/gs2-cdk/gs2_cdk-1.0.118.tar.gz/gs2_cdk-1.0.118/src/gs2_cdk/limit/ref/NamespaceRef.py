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
from .LimitModelRef import LimitModelRef
from ..stamp_sheet.CountDownByUserId import CountDownByUserId
from ..stamp_sheet.DeleteCounterByUserId import DeleteCounterByUserId
from ..stamp_sheet.CountUpByUserId import CountUpByUserId
from ..stamp_sheet.VerifyCounterByUserId import VerifyCounterByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def limit_model(
        self,
        limit_name: str,
    ) -> LimitModelRef:
        return LimitModelRef(
            self.namespace_name,
            limit_name,
        )

    def count_down(
        self,
        limit_name: str,
        counter_name: str,
        count_down_value: Optional[int] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> CountDownByUserId:
        return CountDownByUserId(
            self.namespace_name,
            limit_name,
            counter_name,
            count_down_value,
            user_id,
        )

    def delete_counter(
        self,
        limit_name: str,
        counter_name: str,
        user_id: Optional[str] = "#{userId}",
    ) -> DeleteCounterByUserId:
        return DeleteCounterByUserId(
            self.namespace_name,
            limit_name,
            counter_name,
            user_id,
        )

    def count_up(
        self,
        limit_name: str,
        counter_name: str,
        count_up_value: Optional[int] = None,
        max_value: Optional[int] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> CountUpByUserId:
        return CountUpByUserId(
            self.namespace_name,
            limit_name,
            counter_name,
            count_up_value,
            max_value,
            user_id,
        )

    def verify_counter(
        self,
        limit_name: str,
        counter_name: str,
        verify_type: str,
        count: Optional[int] = None,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyCounterByUserId:
        return VerifyCounterByUserId(
            self.namespace_name,
            limit_name,
            counter_name,
            verify_type,
            count,
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
                "limit",
                self.namespace_name,
            ],
        ).str(
        )
