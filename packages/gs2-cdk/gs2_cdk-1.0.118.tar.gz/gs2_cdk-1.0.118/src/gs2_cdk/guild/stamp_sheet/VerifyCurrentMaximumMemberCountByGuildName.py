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


class VerifyCurrentMaximumMemberCountByGuildName(VerifyAction):

    def __init__(
        self,
        namespace_name: str,
        guild_model_name: str,
        guild_name: str,
        verify_type: str,
        value: Optional[int] = None,
        multiply_value_specifying_quantity: Optional[bool] = None,
    ):
        properties: Dict[str, Any] = {}

        properties["namespaceName"] = namespace_name
        properties["guildModelName"] = guild_model_name
        properties["guildName"] = guild_name
        properties["verifyType"] = verify_type
        properties["value"] = value
        properties["multiplyValueSpecifyingQuantity"] = multiply_value_specifying_quantity

        super().__init__(
            "Gs2Guild:VerifyCurrentMaximumMemberCountByGuildName",
            properties,
        )
