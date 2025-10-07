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
#
# deny overwrite
from .User import User
from .options.UserOptions import UserOptions
from .SecurityPolicy import SecurityPolicy
from .options.SecurityPolicyOptions import SecurityPolicyOptions
from .Identifier import Identifier
from .options.IdentifierOptions import IdentifierOptions
from .Password import Password
from .options.PasswordOptions import PasswordOptions
from .AttachSecurityPolicy import AttachSecurityPolicy
from .options.AttachSecurityPolicyOptions import AttachSecurityPolicyOptions
from .ProjectToken import ProjectToken
from .options.ProjectTokenOptions import ProjectTokenOptions
from .Policy import Policy
from .Statement import Statement