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
from .options.GooglePlayRealtimeNotificationMessageOptions import GooglePlayRealtimeNotificationMessageOptions


class GooglePlayRealtimeNotificationMessage:
    data: str
    message_id: str
    publish_time: str

    def __init__(
        self,
        data: str,
        message_id: str,
        publish_time: str,
        options: Optional[GooglePlayRealtimeNotificationMessageOptions] = GooglePlayRealtimeNotificationMessageOptions(),
    ):
        self.data = data
        self.message_id = message_id
        self.publish_time = publish_time

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.data is not None:
            properties["data"] = self.data
        if self.message_id is not None:
            properties["messageId"] = self.message_id
        if self.publish_time is not None:
            properties["publishTime"] = self.publish_time

        return properties
