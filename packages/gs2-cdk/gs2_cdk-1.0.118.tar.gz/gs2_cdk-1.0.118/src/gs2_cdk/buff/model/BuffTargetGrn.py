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
from .options.BuffTargetGrnOptions import BuffTargetGrnOptions


class BuffTargetGrn:
    target_model_name: str
    target_grn: str

    def __init__(
        self,
        target_model_name: str,
        target_grn: str,
        options: Optional[BuffTargetGrnOptions] = BuffTargetGrnOptions(),
    ):
        self.target_model_name = target_model_name
        self.target_grn = target_grn

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.target_model_name is not None:
            properties["targetModelName"] = self.target_model_name
        if self.target_grn is not None:
            properties["targetGrn"] = self.target_grn

        return properties
