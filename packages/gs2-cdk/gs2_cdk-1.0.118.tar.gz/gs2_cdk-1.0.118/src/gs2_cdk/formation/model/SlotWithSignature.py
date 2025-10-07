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
from .options.SlotWithSignatureOptions import SlotWithSignatureOptions
from .enums.SlotWithSignaturePropertyType import SlotWithSignaturePropertyType


class SlotWithSignature:
    name: str
    property_type: SlotWithSignaturePropertyType
    body: Optional[str] = None
    signature: Optional[str] = None
    metadata: Optional[str] = None

    def __init__(
        self,
        name: str,
        property_type: SlotWithSignaturePropertyType,
        options: Optional[SlotWithSignatureOptions] = SlotWithSignatureOptions(),
    ):
        self.name = name
        self.property_type = property_type
        self.body = options.body if options.body else None
        self.signature = options.signature if options.signature else None
        self.metadata = options.metadata if options.metadata else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.property_type is not None:
            properties["propertyType"] = self.property_type.value
        if self.body is not None:
            properties["body"] = self.body
        if self.signature is not None:
            properties["signature"] = self.signature
        if self.metadata is not None:
            properties["metadata"] = self.metadata

        return properties
