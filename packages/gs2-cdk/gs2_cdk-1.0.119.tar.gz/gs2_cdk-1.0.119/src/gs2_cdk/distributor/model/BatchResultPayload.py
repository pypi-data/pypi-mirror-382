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
from .options.BatchResultPayloadOptions import BatchResultPayloadOptions


class BatchResultPayload:
    request_id: str
    status_code: int
    result_payload: str

    def __init__(
        self,
        request_id: str,
        status_code: int,
        result_payload: str,
        options: Optional[BatchResultPayloadOptions] = BatchResultPayloadOptions(),
    ):
        self.request_id = request_id
        self.status_code = status_code
        self.result_payload = result_payload

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.request_id is not None:
            properties["requestId"] = self.request_id
        if self.status_code is not None:
            properties["statusCode"] = self.status_code
        if self.result_payload is not None:
            properties["resultPayload"] = self.result_payload

        return properties
