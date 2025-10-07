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

from ...core.model import CdkResource, Stack
from .GlobalMessage import GlobalMessage


class CurrentMasterData(CdkResource):
    version: str= "2020-03-12"
    namespace_name: str
    global_messages: List[GlobalMessage]

    def __init__(
        self,
        stack: Stack,
        namespace_name: str,
        global_messages: List[GlobalMessage],
    ):
        super().__init__(
            "Inbox_CurrentMessageMaster_" + namespace_name
        )

        self.namespace_name = namespace_name
        self.global_messages = global_messages
        stack.add_resource(
            self,
        )

    def alternate_keys(
        self,
    ):
        return self.namespace_name

    def resource_type(
        self,
    ) -> str:
        return "GS2::Inbox::CurrentMessageMaster"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}
        settings: Dict[str, Any] = {}

        settings["version"] = self.version
        if self.global_messages is not None:
            settings["globalMessages"] = [
                v.properties(
                )
                for v in self.global_messages
            ]

        if self.namespace_name is not None:
            properties["NamespaceName"] = self.namespace_name
        if settings is not None:
            properties["Settings"] = settings

        return properties