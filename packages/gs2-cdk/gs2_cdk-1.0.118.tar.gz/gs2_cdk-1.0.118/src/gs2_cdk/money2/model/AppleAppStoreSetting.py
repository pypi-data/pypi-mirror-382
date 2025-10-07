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
from .options.AppleAppStoreSettingOptions import AppleAppStoreSettingOptions


class AppleAppStoreSetting:
    bundle_id: Optional[str] = None
    shared_secret_key: Optional[str] = None
    issuer_id: Optional[str] = None
    key_id: Optional[str] = None
    private_key_pem: Optional[str] = None

    def __init__(
        self,
        options: Optional[AppleAppStoreSettingOptions] = AppleAppStoreSettingOptions(),
    ):
        self.bundle_id = options.bundle_id if options.bundle_id else None
        self.shared_secret_key = options.shared_secret_key if options.shared_secret_key else None
        self.issuer_id = options.issuer_id if options.issuer_id else None
        self.key_id = options.key_id if options.key_id else None
        self.private_key_pem = options.private_key_pem if options.private_key_pem else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.bundle_id is not None:
            properties["bundleId"] = self.bundle_id
        if self.shared_secret_key is not None:
            properties["sharedSecretKey"] = self.shared_secret_key
        if self.issuer_id is not None:
            properties["issuerId"] = self.issuer_id
        if self.key_id is not None:
            properties["keyId"] = self.key_id
        if self.private_key_pem is not None:
            properties["privateKeyPem"] = self.private_key_pem

        return properties
