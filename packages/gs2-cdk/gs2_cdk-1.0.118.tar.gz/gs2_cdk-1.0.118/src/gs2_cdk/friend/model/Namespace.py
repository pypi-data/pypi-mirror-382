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
from ...core.model import TransactionSetting
from ...core.model import ScriptSetting
from ...core.model import NotificationSetting
from ...core.model import LogSetting

from ..ref.NamespaceRef import NamespaceRef

from .options.NamespaceOptions import NamespaceOptions


class Namespace(CdkResource):
    stack: Stack
    name: str
    description: Optional[str] = None
    transaction_setting: Optional[TransactionSetting] = None
    follow_script: Optional[ScriptSetting] = None
    unfollow_script: Optional[ScriptSetting] = None
    send_request_script: Optional[ScriptSetting] = None
    cancel_request_script: Optional[ScriptSetting] = None
    accept_request_script: Optional[ScriptSetting] = None
    reject_request_script: Optional[ScriptSetting] = None
    delete_friend_script: Optional[ScriptSetting] = None
    update_profile_script: Optional[ScriptSetting] = None
    follow_notification: Optional[NotificationSetting] = None
    receive_request_notification: Optional[NotificationSetting] = None
    cancel_request_notification: Optional[NotificationSetting] = None
    accept_request_notification: Optional[NotificationSetting] = None
    reject_request_notification: Optional[NotificationSetting] = None
    delete_friend_notification: Optional[NotificationSetting] = None
    log_setting: Optional[LogSetting] = None

    def __init__(
        self,
        stack: Stack,
        name: str,
        options: Optional[NamespaceOptions] = NamespaceOptions(),
    ):
        super().__init__(
            "Friend_Namespace_" + name
        )

        self.stack = stack
        self.name = name
        self.description = options.description if options.description else None
        self.transaction_setting = options.transaction_setting if options.transaction_setting else None
        self.follow_script = options.follow_script if options.follow_script else None
        self.unfollow_script = options.unfollow_script if options.unfollow_script else None
        self.send_request_script = options.send_request_script if options.send_request_script else None
        self.cancel_request_script = options.cancel_request_script if options.cancel_request_script else None
        self.accept_request_script = options.accept_request_script if options.accept_request_script else None
        self.reject_request_script = options.reject_request_script if options.reject_request_script else None
        self.delete_friend_script = options.delete_friend_script if options.delete_friend_script else None
        self.update_profile_script = options.update_profile_script if options.update_profile_script else None
        self.follow_notification = options.follow_notification if options.follow_notification else None
        self.receive_request_notification = options.receive_request_notification if options.receive_request_notification else None
        self.cancel_request_notification = options.cancel_request_notification if options.cancel_request_notification else None
        self.accept_request_notification = options.accept_request_notification if options.accept_request_notification else None
        self.reject_request_notification = options.reject_request_notification if options.reject_request_notification else None
        self.delete_friend_notification = options.delete_friend_notification if options.delete_friend_notification else None
        self.log_setting = options.log_setting if options.log_setting else None
        stack.add_resource(
            self,
        )


    def alternate_keys(
        self,
    ):
        return "name"

    def resource_type(
        self,
    ) -> str:
        return "GS2::Friend::Namespace"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["Name"] = self.name
        if self.description is not None:
            properties["Description"] = self.description
        if self.transaction_setting is not None:
            properties["TransactionSetting"] = self.transaction_setting.properties(
            )
        if self.follow_script is not None:
            properties["FollowScript"] = self.follow_script.properties(
            )
        if self.unfollow_script is not None:
            properties["UnfollowScript"] = self.unfollow_script.properties(
            )
        if self.send_request_script is not None:
            properties["SendRequestScript"] = self.send_request_script.properties(
            )
        if self.cancel_request_script is not None:
            properties["CancelRequestScript"] = self.cancel_request_script.properties(
            )
        if self.accept_request_script is not None:
            properties["AcceptRequestScript"] = self.accept_request_script.properties(
            )
        if self.reject_request_script is not None:
            properties["RejectRequestScript"] = self.reject_request_script.properties(
            )
        if self.delete_friend_script is not None:
            properties["DeleteFriendScript"] = self.delete_friend_script.properties(
            )
        if self.update_profile_script is not None:
            properties["UpdateProfileScript"] = self.update_profile_script.properties(
            )
        if self.follow_notification is not None:
            properties["FollowNotification"] = self.follow_notification.properties(
            )
        if self.receive_request_notification is not None:
            properties["ReceiveRequestNotification"] = self.receive_request_notification.properties(
            )
        if self.cancel_request_notification is not None:
            properties["CancelRequestNotification"] = self.cancel_request_notification.properties(
            )
        if self.accept_request_notification is not None:
            properties["AcceptRequestNotification"] = self.accept_request_notification.properties(
            )
        if self.reject_request_notification is not None:
            properties["RejectRequestNotification"] = self.reject_request_notification.properties(
            )
        if self.delete_friend_notification is not None:
            properties["DeleteFriendNotification"] = self.delete_friend_notification.properties(
            )
        if self.log_setting is not None:
            properties["LogSetting"] = self.log_setting.properties(
            )

        return properties

    def ref(
        self,
    ) -> NamespaceRef:
        return NamespaceRef(
            self.name,
        )

    def get_attr_namespace_id(
        self,
    ) -> GetAttr:
        return GetAttr(
            self,
            "Item.NamespaceId",
            None,
        )
