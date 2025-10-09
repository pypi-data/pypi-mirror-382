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
from .AdMob import AdMob
from .UnityAd import UnityAd
from .AppLovinMax import AppLovinMax
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
    admob: Optional[AdMob] = None
    unity_ad: Optional[UnityAd] = None
    app_lovin_maxes: Optional[List[AppLovinMax]] = None
    acquire_point_script: Optional[ScriptSetting] = None
    consume_point_script: Optional[ScriptSetting] = None
    change_point_notification: Optional[NotificationSetting] = None
    log_setting: Optional[LogSetting] = None

    def __init__(
        self,
        stack: Stack,
        name: str,
        options: Optional[NamespaceOptions] = NamespaceOptions(),
    ):
        super().__init__(
            "AdReward_Namespace_" + name
        )

        self.stack = stack
        self.name = name
        self.description = options.description if options.description else None
        self.transaction_setting = options.transaction_setting if options.transaction_setting else None
        self.admob = options.admob if options.admob else None
        self.unity_ad = options.unity_ad if options.unity_ad else None
        self.app_lovin_maxes = options.app_lovin_maxes if options.app_lovin_maxes else None
        self.acquire_point_script = options.acquire_point_script if options.acquire_point_script else None
        self.consume_point_script = options.consume_point_script if options.consume_point_script else None
        self.change_point_notification = options.change_point_notification if options.change_point_notification else None
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
        return "GS2::AdReward::Namespace"

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
        if self.admob is not None:
            properties["Admob"] = self.admob.properties(
            )
        if self.unity_ad is not None:
            properties["UnityAd"] = self.unity_ad.properties(
            )
        if self.app_lovin_maxes is not None:
            properties["AppLovinMaxes"] = [
                v.properties(
                )
                for v in self.app_lovin_maxes
            ]
        if self.acquire_point_script is not None:
            properties["AcquirePointScript"] = self.acquire_point_script.properties(
            )
        if self.consume_point_script is not None:
            properties["ConsumePointScript"] = self.consume_point_script.properties(
            )
        if self.change_point_notification is not None:
            properties["ChangePointNotification"] = self.change_point_notification.properties(
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
