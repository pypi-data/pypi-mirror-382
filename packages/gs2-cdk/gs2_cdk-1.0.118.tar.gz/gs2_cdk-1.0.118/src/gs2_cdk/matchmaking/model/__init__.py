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
from .Namespace import Namespace
from .options.NamespaceOptions import NamespaceOptions
from .enums.NamespaceEnableDisconnectDetection import NamespaceEnableDisconnectDetection
from .enums.NamespaceCreateGatheringTriggerType import NamespaceCreateGatheringTriggerType
from .enums.NamespaceCompleteMatchmakingTriggerType import NamespaceCompleteMatchmakingTriggerType
from .enums.NamespaceEnableCollaborateSeasonRating import NamespaceEnableCollaborateSeasonRating
from .options.NamespaceEnableDisconnectDetectionIsDisableOptions import NamespaceEnableDisconnectDetectionIsDisableOptions
from .options.NamespaceEnableDisconnectDetectionIsEnableOptions import NamespaceEnableDisconnectDetectionIsEnableOptions
from .options.NamespaceCreateGatheringTriggerTypeIsNoneOptions import NamespaceCreateGatheringTriggerTypeIsNoneOptions
from .options.NamespaceCreateGatheringTriggerTypeIsGs2RealtimeOptions import NamespaceCreateGatheringTriggerTypeIsGs2RealtimeOptions
from .options.NamespaceCreateGatheringTriggerTypeIsGs2ScriptOptions import NamespaceCreateGatheringTriggerTypeIsGs2ScriptOptions
from .options.NamespaceCompleteMatchmakingTriggerTypeIsNoneOptions import NamespaceCompleteMatchmakingTriggerTypeIsNoneOptions
from .options.NamespaceCompleteMatchmakingTriggerTypeIsGs2RealtimeOptions import NamespaceCompleteMatchmakingTriggerTypeIsGs2RealtimeOptions
from .options.NamespaceCompleteMatchmakingTriggerTypeIsGs2ScriptOptions import NamespaceCompleteMatchmakingTriggerTypeIsGs2ScriptOptions
from .options.NamespaceEnableCollaborateSeasonRatingIsEnableOptions import NamespaceEnableCollaborateSeasonRatingIsEnableOptions
from .options.NamespaceEnableCollaborateSeasonRatingIsDisableOptions import NamespaceEnableCollaborateSeasonRatingIsDisableOptions
from .RatingModel import RatingModel
from .options.RatingModelOptions import RatingModelOptions
from .SeasonModel import SeasonModel
from .options.SeasonModelOptions import SeasonModelOptions
from .AttributeRange import AttributeRange
from .options.AttributeRangeOptions import AttributeRangeOptions
from .CapacityOfRole import CapacityOfRole
from .options.CapacityOfRoleOptions import CapacityOfRoleOptions
from .Attribute import Attribute
from .options.AttributeOptions import AttributeOptions
from .Player import Player
from .options.PlayerOptions import PlayerOptions
from .GameResult import GameResult
from .options.GameResultOptions import GameResultOptions
from .SignedBallot import SignedBallot
from .options.SignedBallotOptions import SignedBallotOptions
from .TimeSpan import TimeSpan
from .options.TimeSpanOptions import TimeSpanOptions
from .CurrentMasterData import CurrentMasterData