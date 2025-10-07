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
from .ScopeValue import ScopeValue
from .options.OpenIdConnectSettingOptions import OpenIdConnectSettingOptions


class OpenIdConnectSetting:
    configuration_path: str
    client_id: str
    client_secret: Optional[str] = None
    apple_team_id: Optional[str] = None
    apple_key_id: Optional[str] = None
    apple_private_key_pem: Optional[str] = None
    done_endpoint_url: Optional[str] = None
    additional_scope_values: Optional[List[ScopeValue]] = None
    additional_return_values: Optional[List[str]] = None

    def __init__(
        self,
        configuration_path: str,
        client_id: str,
        options: Optional[OpenIdConnectSettingOptions] = OpenIdConnectSettingOptions(),
    ):
        self.configuration_path = configuration_path
        self.client_id = client_id
        self.client_secret = options.client_secret if options.client_secret else None
        self.apple_team_id = options.apple_team_id if options.apple_team_id else None
        self.apple_key_id = options.apple_key_id if options.apple_key_id else None
        self.apple_private_key_pem = options.apple_private_key_pem if options.apple_private_key_pem else None
        self.done_endpoint_url = options.done_endpoint_url if options.done_endpoint_url else None
        self.additional_scope_values = options.additional_scope_values if options.additional_scope_values else None
        self.additional_return_values = options.additional_return_values if options.additional_return_values else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.configuration_path is not None:
            properties["configurationPath"] = self.configuration_path
        if self.client_id is not None:
            properties["clientId"] = self.client_id
        if self.client_secret is not None:
            properties["clientSecret"] = self.client_secret
        if self.apple_team_id is not None:
            properties["appleTeamId"] = self.apple_team_id
        if self.apple_key_id is not None:
            properties["appleKeyId"] = self.apple_key_id
        if self.apple_private_key_pem is not None:
            properties["applePrivateKeyPem"] = self.apple_private_key_pem
        if self.done_endpoint_url is not None:
            properties["doneEndpointUrl"] = self.done_endpoint_url
        if self.additional_scope_values is not None:
            properties["additionalScopeValues"] = [
                v.properties(
                )
                for v in self.additional_scope_values
            ]
        if self.additional_return_values is not None:
            properties["additionalReturnValues"] = self.additional_return_values

        return properties
