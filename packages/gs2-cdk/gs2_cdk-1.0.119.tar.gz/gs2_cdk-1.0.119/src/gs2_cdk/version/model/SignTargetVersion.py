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
from .options.SignTargetVersionOptions import SignTargetVersionOptions


class SignTargetVersion:
    region: str
    owner_id: str
    namespace_name: str
    version_name: str
    version: Version

    def __init__(
        self,
        region: str,
        owner_id: str,
        namespace_name: str,
        version_name: str,
        version: Version,
        options: Optional[SignTargetVersionOptions] = SignTargetVersionOptions(),
    ):
        self.region = region
        self.owner_id = owner_id
        self.namespace_name = namespace_name
        self.version_name = version_name
        self.version = version

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.region is not None:
            properties["region"] = self.region
        if self.owner_id is not None:
            properties["ownerId"] = self.owner_id
        if self.namespace_name is not None:
            properties["namespaceName"] = self.namespace_name
        if self.version_name is not None:
            properties["versionName"] = self.version_name
        if self.version is not None:
            properties["version"] = self.version.properties(
            )

        return properties
