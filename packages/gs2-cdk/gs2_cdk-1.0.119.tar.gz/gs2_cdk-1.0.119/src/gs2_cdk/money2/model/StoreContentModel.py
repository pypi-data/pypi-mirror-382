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
from .AppleAppStoreContent import AppleAppStoreContent
from .GooglePlayContent import GooglePlayContent
from .options.StoreContentModelOptions import StoreContentModelOptions


class StoreContentModel:
    name: str
    metadata: Optional[str] = None
    apple_app_store: Optional[AppleAppStoreContent] = None
    google_play: Optional[GooglePlayContent] = None

    def __init__(
        self,
        name: str,
        options: Optional[StoreContentModelOptions] = StoreContentModelOptions(),
    ):
        self.name = name
        self.metadata = options.metadata if options.metadata else None
        self.apple_app_store = options.apple_app_store if options.apple_app_store else None
        self.google_play = options.google_play if options.google_play else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.apple_app_store is not None:
            properties["appleAppStore"] = self.apple_app_store.properties(
            )
        if self.google_play is not None:
            properties["googlePlay"] = self.google_play.properties(
            )

        return properties
