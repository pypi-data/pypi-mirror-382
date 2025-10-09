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
from .options.UnityAdOptions import UnityAdOptions


class UnityAd:
    keys: Optional[List[str]] = None

    def __init__(
        self,
        options: Optional[UnityAdOptions] = UnityAdOptions(),
    ):
        self.keys = options.keys if options.keys else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.keys is not None:
            properties["keys"] = self.keys

        return properties
