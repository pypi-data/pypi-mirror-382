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
from .options.GooglePlaySettingOptions import GooglePlaySettingOptions


class GooglePlaySetting:
    package_name: Optional[str] = None
    public_key: Optional[str] = None

    def __init__(
        self,
        options: Optional[GooglePlaySettingOptions] = GooglePlaySettingOptions(),
    ):
        self.package_name = options.package_name if options.package_name else None
        self.public_key = options.public_key if options.public_key else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.package_name is not None:
            properties["packageName"] = self.package_name
        if self.public_key is not None:
            properties["publicKey"] = self.public_key

        return properties
