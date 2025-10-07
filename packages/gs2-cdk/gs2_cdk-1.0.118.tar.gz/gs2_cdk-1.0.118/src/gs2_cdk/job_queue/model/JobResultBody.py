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
from .options.JobResultBodyOptions import JobResultBodyOptions


class JobResultBody:
    try_number: int
    status_code: int
    result: str

    def __init__(
        self,
        try_number: int,
        status_code: int,
        result: str,
        options: Optional[JobResultBodyOptions] = JobResultBodyOptions(),
    ):
        self.try_number = try_number
        self.status_code = status_code
        self.result = result

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.try_number is not None:
            properties["tryNumber"] = self.try_number
        if self.status_code is not None:
            properties["statusCode"] = self.status_code
        if self.result is not None:
            properties["result"] = self.result

        return properties
