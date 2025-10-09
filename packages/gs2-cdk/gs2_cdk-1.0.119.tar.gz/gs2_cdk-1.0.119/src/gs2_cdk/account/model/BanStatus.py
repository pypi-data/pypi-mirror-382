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
from .options.BanStatusOptions import BanStatusOptions


class BanStatus:
    reason: str
    release_timestamp: int

    def __init__(
        self,
        reason: str,
        release_timestamp: int,
        options: Optional[BanStatusOptions] = BanStatusOptions(),
    ):
        self.reason = reason
        self.release_timestamp = release_timestamp

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.reason is not None:
            properties["reason"] = self.reason
        if self.release_timestamp is not None:
            properties["releaseTimestamp"] = self.release_timestamp

        return properties
