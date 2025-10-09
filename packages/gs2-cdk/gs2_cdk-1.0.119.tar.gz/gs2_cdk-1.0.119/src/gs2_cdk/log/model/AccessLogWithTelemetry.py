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
from .options.AccessLogWithTelemetryOptions import AccessLogWithTelemetryOptions
from .enums.AccessLogWithTelemetryStatus import AccessLogWithTelemetryStatus


class AccessLogWithTelemetry:
    timestamp: int
    source_request_id: str
    request_id: str
    duration: int
    service: str
    method: str
    request: str
    result: str
    status: AccessLogWithTelemetryStatus
    user_id: Optional[str] = None

    def __init__(
        self,
        timestamp: int,
        source_request_id: str,
        request_id: str,
        duration: int,
        service: str,
        method: str,
        request: str,
        result: str,
        status: AccessLogWithTelemetryStatus,
        options: Optional[AccessLogWithTelemetryOptions] = AccessLogWithTelemetryOptions(),
    ):
        self.timestamp = timestamp
        self.source_request_id = source_request_id
        self.request_id = request_id
        self.duration = duration
        self.service = service
        self.method = method
        self.request = request
        self.result = result
        self.status = status
        self.user_id = options.user_id if options.user_id else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.timestamp is not None:
            properties["timestamp"] = self.timestamp
        if self.source_request_id is not None:
            properties["sourceRequestId"] = self.source_request_id
        if self.request_id is not None:
            properties["requestId"] = self.request_id
        if self.duration is not None:
            properties["duration"] = self.duration
        if self.service is not None:
            properties["service"] = self.service
        if self.method is not None:
            properties["method"] = self.method
        if self.user_id is not None:
            properties["userId"] = self.user_id
        if self.request is not None:
            properties["request"] = self.request
        if self.result is not None:
            properties["result"] = self.result
        if self.status is not None:
            properties["status"] = self.status.value

        return properties
