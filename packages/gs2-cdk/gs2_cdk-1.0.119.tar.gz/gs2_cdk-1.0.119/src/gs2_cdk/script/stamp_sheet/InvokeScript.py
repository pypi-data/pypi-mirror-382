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
from ..model.RandomStatus import RandomStatus


class InvokeScript(AcquireAction):

    def __init__(
        self,
        script_id: str,
        args: Optional[str] = None,
        random_status: Optional[RandomStatus] = None,
        user_id: Optional[str] = "#{userId}",
    ):
        properties: Dict[str, Any] = {}

        properties["scriptId"] = script_id
        properties["args"] = args
        properties["randomStatus"] = random_status
        properties["userId"] = user_id

        super().__init__(
            "Gs2Script:InvokeScript",
            properties,
        )
