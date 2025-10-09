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
from ...core.func import GetAttr

from ..ref.KeyRef import KeyRef

from .options.KeyOptions import KeyOptions


class Key(CdkResource):
    stack: Stack
    namespace_name: str
    name: str
    description: Optional[str] = None

    def __init__(
        self,
        stack: Stack,
        namespace_name: str,
        name: str,
        options: Optional[KeyOptions] = KeyOptions(),
    ):
        super().__init__(
            "Key_Key_" + name
        )

        self.stack = stack
        self.namespace_name = namespace_name
        self.name = name
        self.description = options.description if options.description else None
        stack.add_resource(
            self,
        )


    def alternate_keys(
        self,
    ):
        return "name"

    def resource_type(
        self,
    ) -> str:
        return "GS2::Key::Key"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.namespace_name is not None:
            properties["NamespaceName"] = self.namespace_name
        if self.name is not None:
            properties["Name"] = self.name
        if self.description is not None:
            properties["Description"] = self.description

        return properties

    def ref(
        self,
    ) -> KeyRef:
        return KeyRef(
            self.namespace_name,
            self.name,
        )

    def get_attr_key_id(
        self,
    ) -> GetAttr:
        return GetAttr(
            self,
            "Item.KeyId",
            None,
        )
