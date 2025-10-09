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
from .options.AutoRunTransactionSettingOptions import AutoRunTransactionSettingOptions


class AutoRunTransactionSetting:
    distributor_namespace_id: str
    queue_namespace_id: Optional[str] = None

    def __init__(
        self,
        distributor_namespace_id: str,
        options: Optional[AutoRunTransactionSettingOptions] = AutoRunTransactionSettingOptions(),
    ):
        self.distributor_namespace_id = distributor_namespace_id
        self.queue_namespace_id = options.queue_namespace_id if options.queue_namespace_id else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.distributor_namespace_id is not None:
            properties["distributorNamespaceId"] = self.distributor_namespace_id
        if self.queue_namespace_id is not None:
            properties["queueNamespaceId"] = self.queue_namespace_id

        return properties
