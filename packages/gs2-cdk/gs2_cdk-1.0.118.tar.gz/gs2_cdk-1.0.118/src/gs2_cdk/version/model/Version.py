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
from .options.VersionOptions import VersionOptions


class Version:
    major: int
    minor: int
    micro: int

    def __init__(
        self,
        major: int,
        minor: int,
        micro: int,
        options: Optional[VersionOptions] = VersionOptions(),
    ):
        self.major = major
        self.minor = minor
        self.micro = micro

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.major is not None:
            properties["major"] = self.major
        if self.minor is not None:
            properties["minor"] = self.minor
        if self.micro is not None:
            properties["micro"] = self.micro

        return properties
