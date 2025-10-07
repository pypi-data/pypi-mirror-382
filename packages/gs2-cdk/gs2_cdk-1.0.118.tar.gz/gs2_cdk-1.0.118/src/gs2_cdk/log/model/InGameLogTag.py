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
from .options.InGameLogTagOptions import InGameLogTagOptions


class InGameLogTag:
    key: str
    value: str

    def __init__(
        self,
        key: str,
        value: str,
        options: Optional[InGameLogTagOptions] = InGameLogTagOptions(),
    ):
        self.key = key
        self.value = value

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.key is not None:
            properties["key"] = self.key
        if self.value is not None:
            properties["value"] = self.value

        return properties
