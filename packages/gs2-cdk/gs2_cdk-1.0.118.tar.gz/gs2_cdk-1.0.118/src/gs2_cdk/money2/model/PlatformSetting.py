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
from .AppleAppStoreSetting import AppleAppStoreSetting
from .GooglePlaySetting import GooglePlaySetting
from .FakeSetting import FakeSetting
from .options.PlatformSettingOptions import PlatformSettingOptions


class PlatformSetting:
    apple_app_store: Optional[AppleAppStoreSetting] = None
    google_play: Optional[GooglePlaySetting] = None
    fake: Optional[FakeSetting] = None

    def __init__(
        self,
        options: Optional[PlatformSettingOptions] = PlatformSettingOptions(),
    ):
        self.apple_app_store = options.apple_app_store if options.apple_app_store else None
        self.google_play = options.google_play if options.google_play else None
        self.fake = options.fake if options.fake else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.apple_app_store is not None:
            properties["appleAppStore"] = self.apple_app_store.properties(
            )
        if self.google_play is not None:
            properties["googlePlay"] = self.google_play.properties(
            )
        if self.fake is not None:
            properties["fake"] = self.fake.properties(
            )

        return properties
