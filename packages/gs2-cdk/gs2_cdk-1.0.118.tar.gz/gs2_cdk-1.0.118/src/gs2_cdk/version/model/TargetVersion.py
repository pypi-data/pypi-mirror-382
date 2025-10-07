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
from .Version import Version
from .options.TargetVersionOptions import TargetVersionOptions


class TargetVersion:
    version_name: str
    body: Optional[str] = None
    signature: Optional[str] = None
    version: Optional[Version] = None

    def __init__(
        self,
        version_name: str,
        options: Optional[TargetVersionOptions] = TargetVersionOptions(),
    ):
        self.version_name = version_name
        self.body = options.body if options.body else None
        self.signature = options.signature if options.signature else None
        self.version = options.version if options.version else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.version_name is not None:
            properties["versionName"] = self.version_name
        if self.body is not None:
            properties["body"] = self.body
        if self.signature is not None:
            properties["signature"] = self.signature
        if self.version is not None:
            properties["version"] = self.version.properties(
            )

        return properties
