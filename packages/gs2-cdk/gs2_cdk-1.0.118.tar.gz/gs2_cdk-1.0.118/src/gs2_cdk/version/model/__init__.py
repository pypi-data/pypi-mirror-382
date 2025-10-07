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
from .VersionModel import VersionModel
from .options.VersionModelOptions import VersionModelOptions
from .enums.VersionModelScope import VersionModelScope
from .enums.VersionModelType import VersionModelType
from .enums.VersionModelApproveRequirement import VersionModelApproveRequirement
from .options.VersionModelTypeIsSimpleOptions import VersionModelTypeIsSimpleOptions
from .options.VersionModelTypeIsScheduleOptions import VersionModelTypeIsScheduleOptions
from .options.VersionModelScopeIsPassiveOptions import VersionModelScopeIsPassiveOptions
from .options.VersionModelScopeIsActiveOptions import VersionModelScopeIsActiveOptions
from .Status import Status
from .options.StatusOptions import StatusOptions
from .TargetVersion import TargetVersion
from .options.TargetVersionOptions import TargetVersionOptions
from .SignTargetVersion import SignTargetVersion
from .options.SignTargetVersionOptions import SignTargetVersionOptions
from .Version import Version
from .options.VersionOptions import VersionOptions
from .ScheduleVersion import ScheduleVersion
from .options.ScheduleVersionOptions import ScheduleVersionOptions
from .CurrentMasterData import CurrentMasterData