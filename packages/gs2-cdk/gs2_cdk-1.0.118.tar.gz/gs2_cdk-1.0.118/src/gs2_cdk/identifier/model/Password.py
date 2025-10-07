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

from ..ref.PasswordRef import PasswordRef
from .enums.PasswordEnableTwoFactorAuthentication import PasswordEnableTwoFactorAuthentication

from .options.PasswordOptions import PasswordOptions


class Password(CdkResource):
    stack: Stack
    user_name: str
    password: str

    def __init__(
        self,
        stack: Stack,
        user_name: str,
        password: str,
        options: Optional[PasswordOptions] = PasswordOptions(),
    ):
        super().__init__(
            "Identifier_Password_"
        )

        self.stack = stack
        self.user_name = user_name
        self.password = password
        stack.add_resource(
            self,
        )


    def alternate_keys(
        self,
    ):
        return ""

    def resource_type(
        self,
    ) -> str:
        return "GS2::Identifier::Password"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.user_name is not None:
            properties["UserName"] = self.user_name
        if self.password is not None:
            properties["Password"] = self.password

        return properties

    def ref(
        self,
    ) -> PasswordRef:
        return PasswordRef(
            self.user_name,
        )

    def get_attr_password_id(
        self,
    ) -> GetAttr:
        return GetAttr(
            self,
            "Item.PasswordId",
            None,
        )
