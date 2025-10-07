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

from ..ref.ScriptRef import ScriptRef

from .options.ScriptOptions import ScriptOptions


class Script(CdkResource):
    stack: Stack
    namespace_name: str
    name: str
    script: str
    description: Optional[str] = None
    disable_string_number_to_number: Optional[bool] = None

    def __init__(
        self,
        stack: Stack,
        namespace_name: str,
        name: str,
        script: str,
        options: Optional[ScriptOptions] = ScriptOptions(),
    ):
        super().__init__(
            "Script_Script_" + name
        )

        self.stack = stack
        self.namespace_name = namespace_name
        self.name = name
        self.script = script
        self.description = options.description if options.description else None
        self.disable_string_number_to_number = options.disable_string_number_to_number if options.disable_string_number_to_number else None
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
        return "GS2::Script::Script"

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
        if self.script is not None:
            properties["Script"] = self.script
        if self.disable_string_number_to_number is not None:
            properties["DisableStringNumberToNumber"] = self.disable_string_number_to_number

        return properties

    def ref(
        self,
    ) -> ScriptRef:
        return ScriptRef(
            self.namespace_name,
            self.name,
        )

    def get_attr_script_id(
        self,
    ) -> GetAttr:
        return GetAttr(
            self,
            "Item.ScriptId",
            None,
        )
