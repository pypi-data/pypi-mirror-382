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
from .options.SendNotificationEntryOptions import SendNotificationEntryOptions


class SendNotificationEntry:
    user_id: str
    issuer: str
    subject: str
    payload: str
    enable_transfer_mobile_notification: bool
    sound: Optional[str] = None

    def __init__(
        self,
        user_id: str,
        issuer: str,
        subject: str,
        payload: str,
        enable_transfer_mobile_notification: bool,
        options: Optional[SendNotificationEntryOptions] = SendNotificationEntryOptions(),
    ):
        self.user_id = user_id
        self.issuer = issuer
        self.subject = subject
        self.payload = payload
        self.enable_transfer_mobile_notification = enable_transfer_mobile_notification
        self.sound = options.sound if options.sound else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.user_id is not None:
            properties["userId"] = self.user_id
        if self.issuer is not None:
            properties["issuer"] = self.issuer
        if self.subject is not None:
            properties["subject"] = self.subject
        if self.payload is not None:
            properties["payload"] = self.payload
        if self.enable_transfer_mobile_notification is not None:
            properties["enableTransferMobileNotification"] = self.enable_transfer_mobile_notification
        if self.sound is not None:
            properties["sound"] = self.sound

        return properties
