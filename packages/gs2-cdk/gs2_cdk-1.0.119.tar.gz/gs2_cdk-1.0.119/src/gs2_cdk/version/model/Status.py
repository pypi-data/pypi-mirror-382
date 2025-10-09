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
from .ScheduleVersion import ScheduleVersion
from .VersionModel import VersionModel
from .options.StatusOptions import StatusOptions


class Status:
    version_model: VersionModel
    current_version: Optional[Version] = None

    def __init__(
        self,
        version_model: VersionModel,
        options: Optional[StatusOptions] = StatusOptions(),
    ):
        self.version_model = version_model
        self.current_version = options.current_version if options.current_version else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.version_model is not None:
            properties["versionModel"] = self.version_model.properties(
            )
        if self.current_version is not None:
            properties["currentVersion"] = self.current_version.properties(
            )

        return properties
