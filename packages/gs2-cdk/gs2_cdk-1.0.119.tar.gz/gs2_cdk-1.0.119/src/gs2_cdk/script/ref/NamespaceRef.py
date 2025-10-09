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
from .ScriptRef import ScriptRef
from ..stamp_sheet.InvokeScript import InvokeScript
from ..model.RandomStatus import RandomStatus


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def invoke_script(
        self,
        script_id: str,
        args: Optional[str] = None,
        random_status: Optional[RandomStatus] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> InvokeScript:
        return InvokeScript(
            script_id,
            args,
            random_status,
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
                "script",
                self.namespace_name,
            ],
        ).str(
        )
