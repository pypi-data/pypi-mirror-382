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
from .options.ProgressOptions import ProgressOptions


class Progress:
    upload_token: str
    generated: int
    pattern_count: int
    revision: Optional[int] = None

    def __init__(
        self,
        upload_token: str,
        generated: int,
        pattern_count: int,
        options: Optional[ProgressOptions] = ProgressOptions(),
    ):
        self.upload_token = upload_token
        self.generated = generated
        self.pattern_count = pattern_count
        self.revision = options.revision if options.revision else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.upload_token is not None:
            properties["uploadToken"] = self.upload_token
        if self.generated is not None:
            properties["generated"] = self.generated
        if self.pattern_count is not None:
            properties["patternCount"] = self.pattern_count

        return properties
