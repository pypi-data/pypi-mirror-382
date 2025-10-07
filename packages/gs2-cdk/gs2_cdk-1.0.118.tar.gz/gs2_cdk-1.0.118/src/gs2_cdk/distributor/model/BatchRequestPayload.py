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
from .options.BatchRequestPayloadOptions import BatchRequestPayloadOptions
from .enums.BatchRequestPayloadService import BatchRequestPayloadService


class BatchRequestPayload:
    request_id: str
    service: BatchRequestPayloadService
    method_name: str
    parameter: str

    def __init__(
        self,
        request_id: str,
        service: BatchRequestPayloadService,
        method_name: str,
        parameter: str,
        options: Optional[BatchRequestPayloadOptions] = BatchRequestPayloadOptions(),
    ):
        self.request_id = request_id
        self.service = service
        self.method_name = method_name
        self.parameter = parameter

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.request_id is not None:
            properties["requestId"] = self.request_id
        if self.service is not None:
            properties["service"] = self.service.value
        if self.method_name is not None:
            properties["methodName"] = self.method_name
        if self.parameter is not None:
            properties["parameter"] = self.parameter

        return properties
