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
from .options.FakeSettingOptions import FakeSettingOptions
from .enums.FakeSettingAcceptFakeReceipt import FakeSettingAcceptFakeReceipt


class FakeSetting:
    accept_fake_receipt: FakeSettingAcceptFakeReceipt

    def __init__(
        self,
        accept_fake_receipt: FakeSettingAcceptFakeReceipt,
        options: Optional[FakeSettingOptions] = FakeSettingOptions(),
    ):
        self.accept_fake_receipt = accept_fake_receipt

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.accept_fake_receipt is not None:
            properties["acceptFakeReceipt"] = self.accept_fake_receipt.value

        return properties
