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

from ...core.model import AcquireAction, ConsumeAction, VerifyAction


class VerifyCounterByUserId(VerifyAction):

    def __init__(
        self,
        namespace_name: str,
        limit_name: str,
        counter_name: str,
        verify_type: str,
        count: Optional[int] = None,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ):
        properties: Dict[str, Any] = {}

        properties["namespaceName"] = namespace_name
        properties["limitName"] = limit_name
        properties["counterName"] = counter_name
        properties["verifyType"] = verify_type
        properties["count"] = count
        properties["multiplyValueSpecifyingQuantity"] = multiply_value_specifying_quantity
        properties["userId"] = user_id

        super().__init__(
            "Gs2Limit:VerifyCounterByUserId",
            properties,
        )
