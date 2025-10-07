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
from .CurrentMasterData import CurrentMasterData
from .RatingModel import RatingModel
from .SeasonModel import SeasonModel
from .enums.NamespaceEnableDisconnectDetection import NamespaceEnableDisconnectDetection
from .enums.NamespaceCreateGatheringTriggerType import NamespaceCreateGatheringTriggerType
from .enums.NamespaceCompleteMatchmakingTriggerType import NamespaceCompleteMatchmakingTriggerType
from .enums.NamespaceEnableCollaborateSeasonRating import NamespaceEnableCollaborateSeasonRating

from .options.NamespaceOptions import NamespaceOptions


class Namespace(CdkResource):
    stack: Stack
    name: str
    create_gathering_trigger_type: NamespaceCreateGatheringTriggerType
    complete_matchmaking_trigger_type: NamespaceCompleteMatchmakingTriggerType
    description: Optional[str] = None
    transaction_setting: Optional[TransactionSetting] = None
    enable_rating: Optional[bool] = None
    enable_disconnect_detection: Optional[NamespaceEnableDisconnectDetection] = None
    disconnect_detection_timeout_seconds: Optional[int] = None
    create_gathering_trigger_realtime_namespace_id: Optional[str] = None
    create_gathering_trigger_script_id: Optional[str] = None
    complete_matchmaking_trigger_realtime_namespace_id: Optional[str] = None
    complete_matchmaking_trigger_script_id: Optional[str] = None
    enable_collaborate_season_rating: Optional[NamespaceEnableCollaborateSeasonRating] = None
    collaborate_season_rating_namespace_id: Optional[str] = None
    collaborate_season_rating_ttl: Optional[int] = None
    change_rating_script: Optional[ScriptSetting] = None
    join_notification: Optional[NotificationSetting] = None
    leave_notification: Optional[NotificationSetting] = None
    complete_notification: Optional[NotificationSetting] = None
    change_rating_notification: Optional[NotificationSetting] = None
    log_setting: Optional[LogSetting] = None

    def __init__(
        self,
        stack: Stack,
        name: str,
        create_gathering_trigger_type: NamespaceCreateGatheringTriggerType,
        complete_matchmaking_trigger_type: NamespaceCompleteMatchmakingTriggerType,
        options: Optional[NamespaceOptions] = NamespaceOptions(),
    ):
        super().__init__(
            "Matchmaking_Namespace_" + name
        )

        self.stack = stack
        self.name = name
        self.create_gathering_trigger_type = create_gathering_trigger_type
        self.complete_matchmaking_trigger_type = complete_matchmaking_trigger_type
        self.description = options.description if options.description else None
        self.transaction_setting = options.transaction_setting if options.transaction_setting else None
        self.enable_rating = options.enable_rating if options.enable_rating else None
        self.enable_disconnect_detection = options.enable_disconnect_detection if options.enable_disconnect_detection else None
        self.disconnect_detection_timeout_seconds = options.disconnect_detection_timeout_seconds if options.disconnect_detection_timeout_seconds else None
        self.create_gathering_trigger_realtime_namespace_id = options.create_gathering_trigger_realtime_namespace_id if options.create_gathering_trigger_realtime_namespace_id else None
        self.create_gathering_trigger_script_id = options.create_gathering_trigger_script_id if options.create_gathering_trigger_script_id else None
        self.complete_matchmaking_trigger_realtime_namespace_id = options.complete_matchmaking_trigger_realtime_namespace_id if options.complete_matchmaking_trigger_realtime_namespace_id else None
        self.complete_matchmaking_trigger_script_id = options.complete_matchmaking_trigger_script_id if options.complete_matchmaking_trigger_script_id else None
        self.enable_collaborate_season_rating = options.enable_collaborate_season_rating if options.enable_collaborate_season_rating else None
        self.collaborate_season_rating_namespace_id = options.collaborate_season_rating_namespace_id if options.collaborate_season_rating_namespace_id else None
        self.collaborate_season_rating_ttl = options.collaborate_season_rating_ttl if options.collaborate_season_rating_ttl else None
        self.change_rating_script = options.change_rating_script if options.change_rating_script else None
        self.join_notification = options.join_notification if options.join_notification else None
        self.leave_notification = options.leave_notification if options.leave_notification else None
        self.complete_notification = options.complete_notification if options.complete_notification else None
        self.change_rating_notification = options.change_rating_notification if options.change_rating_notification else None
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
        return "GS2::Matchmaking::Namespace"

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
        if self.enable_rating is not None:
            properties["EnableRating"] = self.enable_rating
        if self.enable_disconnect_detection is not None:
            properties["EnableDisconnectDetection"] = self.enable_disconnect_detection
        if self.disconnect_detection_timeout_seconds is not None:
            properties["DisconnectDetectionTimeoutSeconds"] = self.disconnect_detection_timeout_seconds
        if self.create_gathering_trigger_type is not None:
            properties["CreateGatheringTriggerType"] = self.create_gathering_trigger_type
        if self.create_gathering_trigger_realtime_namespace_id is not None:
            properties["CreateGatheringTriggerRealtimeNamespaceId"] = self.create_gathering_trigger_realtime_namespace_id
        if self.create_gathering_trigger_script_id is not None:
            properties["CreateGatheringTriggerScriptId"] = self.create_gathering_trigger_script_id
        if self.complete_matchmaking_trigger_type is not None:
            properties["CompleteMatchmakingTriggerType"] = self.complete_matchmaking_trigger_type
        if self.complete_matchmaking_trigger_realtime_namespace_id is not None:
            properties["CompleteMatchmakingTriggerRealtimeNamespaceId"] = self.complete_matchmaking_trigger_realtime_namespace_id
        if self.complete_matchmaking_trigger_script_id is not None:
            properties["CompleteMatchmakingTriggerScriptId"] = self.complete_matchmaking_trigger_script_id
        if self.enable_collaborate_season_rating is not None:
            properties["EnableCollaborateSeasonRating"] = self.enable_collaborate_season_rating
        if self.collaborate_season_rating_namespace_id is not None:
            properties["CollaborateSeasonRatingNamespaceId"] = self.collaborate_season_rating_namespace_id
        if self.collaborate_season_rating_ttl is not None:
            properties["CollaborateSeasonRatingTtl"] = self.collaborate_season_rating_ttl
        if self.change_rating_script is not None:
            properties["ChangeRatingScript"] = self.change_rating_script.properties(
            )
        if self.join_notification is not None:
            properties["JoinNotification"] = self.join_notification.properties(
            )
        if self.leave_notification is not None:
            properties["LeaveNotification"] = self.leave_notification.properties(
            )
        if self.complete_notification is not None:
            properties["CompleteNotification"] = self.complete_notification.properties(
            )
        if self.change_rating_notification is not None:
            properties["ChangeRatingNotification"] = self.change_rating_notification.properties(
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

    def master_data(
        self,
        rating_models: List[RatingModel],
        season_models: List[SeasonModel],
    ) -> Namespace:
        CurrentMasterData(
            self.stack,
            self.name,
            rating_models,
            season_models,
        ).add_depends_on(
            self,
        )
        return self
