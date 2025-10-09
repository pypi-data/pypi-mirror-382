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
from .options.PlatformUserOptions import PlatformUserOptions


class PlatformUser:
    type: int
    user_identifier: str
    user_id: str

    def __init__(
        self,
        type: int,
        user_identifier: str,
        user_id: str,
        options: Optional[PlatformUserOptions] = PlatformUserOptions(),
    ):
        self.type = type
        self.user_identifier = user_identifier
        self.user_id = user_id

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.type is not None:
            properties["type"] = self.type
        if self.user_identifier is not None:
            properties["userIdentifier"] = self.user_identifier
        if self.user_id is not None:
            properties["userId"] = self.user_id

        return properties
