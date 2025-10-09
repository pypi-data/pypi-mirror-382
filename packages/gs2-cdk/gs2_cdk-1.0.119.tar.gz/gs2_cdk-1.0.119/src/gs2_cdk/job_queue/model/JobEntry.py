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
from .options.JobEntryOptions import JobEntryOptions


class JobEntry:
    script_id: str
    args: str
    max_try_count: int

    def __init__(
        self,
        script_id: str,
        args: str,
        max_try_count: int,
        options: Optional[JobEntryOptions] = JobEntryOptions(),
    ):
        self.script_id = script_id
        self.args = args
        self.max_try_count = max_try_count

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.script_id is not None:
            properties["scriptId"] = self.script_id
        if self.args is not None:
            properties["args"] = self.args
        if self.max_try_count is not None:
            properties["maxTryCount"] = self.max_try_count

        return properties
