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
from .options.BlockingPolicyModelOptions import BlockingPolicyModelOptions
from .options.BlockingPolicyModelLocationDetectionIsEnableOptions import BlockingPolicyModelLocationDetectionIsEnableOptions
from .options.BlockingPolicyModelLocationDetectionIsDisableOptions import BlockingPolicyModelLocationDetectionIsDisableOptions
from .options.BlockingPolicyModelAnonymousIpDetectionIsEnableOptions import BlockingPolicyModelAnonymousIpDetectionIsEnableOptions
from .options.BlockingPolicyModelAnonymousIpDetectionIsDisableOptions import BlockingPolicyModelAnonymousIpDetectionIsDisableOptions
from .options.BlockingPolicyModelHostingProviderIpDetectionIsEnableOptions import BlockingPolicyModelHostingProviderIpDetectionIsEnableOptions
from .options.BlockingPolicyModelHostingProviderIpDetectionIsDisableOptions import BlockingPolicyModelHostingProviderIpDetectionIsDisableOptions
from .options.BlockingPolicyModelReputationIpDetectionIsEnableOptions import BlockingPolicyModelReputationIpDetectionIsEnableOptions
from .options.BlockingPolicyModelReputationIpDetectionIsDisableOptions import BlockingPolicyModelReputationIpDetectionIsDisableOptions
from .options.BlockingPolicyModelIpAddressesDetectionIsEnableOptions import BlockingPolicyModelIpAddressesDetectionIsEnableOptions
from .options.BlockingPolicyModelIpAddressesDetectionIsDisableOptions import BlockingPolicyModelIpAddressesDetectionIsDisableOptions
from .enums.BlockingPolicyModelDefaultRestriction import BlockingPolicyModelDefaultRestriction
from .enums.BlockingPolicyModelLocationDetection import BlockingPolicyModelLocationDetection
from .enums.BlockingPolicyModelLocationRestriction import BlockingPolicyModelLocationRestriction
from .enums.BlockingPolicyModelAnonymousIpDetection import BlockingPolicyModelAnonymousIpDetection
from .enums.BlockingPolicyModelAnonymousIpRestriction import BlockingPolicyModelAnonymousIpRestriction
from .enums.BlockingPolicyModelHostingProviderIpDetection import BlockingPolicyModelHostingProviderIpDetection
from .enums.BlockingPolicyModelHostingProviderIpRestriction import BlockingPolicyModelHostingProviderIpRestriction
from .enums.BlockingPolicyModelReputationIpDetection import BlockingPolicyModelReputationIpDetection
from .enums.BlockingPolicyModelReputationIpRestriction import BlockingPolicyModelReputationIpRestriction
from .enums.BlockingPolicyModelIpAddressesDetection import BlockingPolicyModelIpAddressesDetection
from .enums.BlockingPolicyModelIpAddressRestriction import BlockingPolicyModelIpAddressRestriction


class BlockingPolicyModel:
    pass_services: List[str]
    default_restriction: BlockingPolicyModelDefaultRestriction
    location_detection: BlockingPolicyModelLocationDetection
    anonymous_ip_detection: BlockingPolicyModelAnonymousIpDetection
    hosting_provider_ip_detection: BlockingPolicyModelHostingProviderIpDetection
    reputation_ip_detection: BlockingPolicyModelReputationIpDetection
    ip_addresses_detection: BlockingPolicyModelIpAddressesDetection
    locations: Optional[List[str]] = None
    location_restriction: Optional[BlockingPolicyModelLocationRestriction] = None
    anonymous_ip_restriction: Optional[BlockingPolicyModelAnonymousIpRestriction] = None
    hosting_provider_ip_restriction: Optional[BlockingPolicyModelHostingProviderIpRestriction] = None
    reputation_ip_restriction: Optional[BlockingPolicyModelReputationIpRestriction] = None
    ip_addresses: Optional[List[str]] = None
    ip_address_restriction: Optional[BlockingPolicyModelIpAddressRestriction] = None

    def __init__(
        self,
        pass_services: List[str],
        default_restriction: BlockingPolicyModelDefaultRestriction,
        location_detection: BlockingPolicyModelLocationDetection,
        anonymous_ip_detection: BlockingPolicyModelAnonymousIpDetection,
        hosting_provider_ip_detection: BlockingPolicyModelHostingProviderIpDetection,
        reputation_ip_detection: BlockingPolicyModelReputationIpDetection,
        ip_addresses_detection: BlockingPolicyModelIpAddressesDetection,
        options: Optional[BlockingPolicyModelOptions] = BlockingPolicyModelOptions(),
    ):
        self.pass_services = pass_services
        self.default_restriction = default_restriction
        self.location_detection = location_detection
        self.anonymous_ip_detection = anonymous_ip_detection
        self.hosting_provider_ip_detection = hosting_provider_ip_detection
        self.reputation_ip_detection = reputation_ip_detection
        self.ip_addresses_detection = ip_addresses_detection
        self.locations = options.locations if options.locations else None
        self.location_restriction = options.location_restriction if options.location_restriction else None
        self.anonymous_ip_restriction = options.anonymous_ip_restriction if options.anonymous_ip_restriction else None
        self.hosting_provider_ip_restriction = options.hosting_provider_ip_restriction if options.hosting_provider_ip_restriction else None
        self.reputation_ip_restriction = options.reputation_ip_restriction if options.reputation_ip_restriction else None
        self.ip_addresses = options.ip_addresses if options.ip_addresses else None
        self.ip_address_restriction = options.ip_address_restriction if options.ip_address_restriction else None

    @staticmethod
    def location_detection_is_enable(
        pass_services: List[str],
        default_restriction: BlockingPolicyModelDefaultRestriction,
        anonymous_ip_detection: BlockingPolicyModelAnonymousIpDetection,
        hosting_provider_ip_detection: BlockingPolicyModelHostingProviderIpDetection,
        reputation_ip_detection: BlockingPolicyModelReputationIpDetection,
        ip_addresses_detection: BlockingPolicyModelIpAddressesDetection,
        locations: List[str],
        location_restriction: BlockingPolicyModelLocationRestriction,
        options: Optional[BlockingPolicyModelLocationDetectionIsEnableOptions] = BlockingPolicyModelLocationDetectionIsEnableOptions(),
    ) -> BlockingPolicyModel:
        return BlockingPolicyModel(
            pass_services,
            default_restriction,
            BlockingPolicyModelLocationDetection.ENABLE,
            anonymous_ip_detection,
            hosting_provider_ip_detection,
            reputation_ip_detection,
            ip_addresses_detection,
            BlockingPolicyModelOptions(
                locations,
                location_restriction,
                options.ip_addresses,
            ),
        )

    @staticmethod
    def location_detection_is_disable(
        pass_services: List[str],
        default_restriction: BlockingPolicyModelDefaultRestriction,
        anonymous_ip_detection: BlockingPolicyModelAnonymousIpDetection,
        hosting_provider_ip_detection: BlockingPolicyModelHostingProviderIpDetection,
        reputation_ip_detection: BlockingPolicyModelReputationIpDetection,
        ip_addresses_detection: BlockingPolicyModelIpAddressesDetection,
        options: Optional[BlockingPolicyModelLocationDetectionIsDisableOptions] = BlockingPolicyModelLocationDetectionIsDisableOptions(),
    ) -> BlockingPolicyModel:
        return BlockingPolicyModel(
            pass_services,
            default_restriction,
            BlockingPolicyModelLocationDetection.DISABLE,
            anonymous_ip_detection,
            hosting_provider_ip_detection,
            reputation_ip_detection,
            ip_addresses_detection,
            BlockingPolicyModelOptions(
                options.ip_addresses,
            ),
        )

    @staticmethod
    def anonymous_ip_detection_is_enable(
        pass_services: List[str],
        default_restriction: BlockingPolicyModelDefaultRestriction,
        location_detection: BlockingPolicyModelLocationDetection,
        hosting_provider_ip_detection: BlockingPolicyModelHostingProviderIpDetection,
        reputation_ip_detection: BlockingPolicyModelReputationIpDetection,
        ip_addresses_detection: BlockingPolicyModelIpAddressesDetection,
        anonymous_ip_restriction: BlockingPolicyModelAnonymousIpRestriction,
        options: Optional[BlockingPolicyModelAnonymousIpDetectionIsEnableOptions] = BlockingPolicyModelAnonymousIpDetectionIsEnableOptions(),
    ) -> BlockingPolicyModel:
        return BlockingPolicyModel(
            pass_services,
            default_restriction,
            location_detection,
            BlockingPolicyModelAnonymousIpDetection.ENABLE,
            hosting_provider_ip_detection,
            reputation_ip_detection,
            ip_addresses_detection,
            BlockingPolicyModelOptions(
                anonymous_ip_restriction,
                options.ip_addresses,
            ),
        )

    @staticmethod
    def anonymous_ip_detection_is_disable(
        pass_services: List[str],
        default_restriction: BlockingPolicyModelDefaultRestriction,
        location_detection: BlockingPolicyModelLocationDetection,
        hosting_provider_ip_detection: BlockingPolicyModelHostingProviderIpDetection,
        reputation_ip_detection: BlockingPolicyModelReputationIpDetection,
        ip_addresses_detection: BlockingPolicyModelIpAddressesDetection,
        options: Optional[BlockingPolicyModelAnonymousIpDetectionIsDisableOptions] = BlockingPolicyModelAnonymousIpDetectionIsDisableOptions(),
    ) -> BlockingPolicyModel:
        return BlockingPolicyModel(
            pass_services,
            default_restriction,
            location_detection,
            BlockingPolicyModelAnonymousIpDetection.DISABLE,
            hosting_provider_ip_detection,
            reputation_ip_detection,
            ip_addresses_detection,
            BlockingPolicyModelOptions(
                options.ip_addresses,
            ),
        )

    @staticmethod
    def hosting_provider_ip_detection_is_enable(
        pass_services: List[str],
        default_restriction: BlockingPolicyModelDefaultRestriction,
        location_detection: BlockingPolicyModelLocationDetection,
        anonymous_ip_detection: BlockingPolicyModelAnonymousIpDetection,
        reputation_ip_detection: BlockingPolicyModelReputationIpDetection,
        ip_addresses_detection: BlockingPolicyModelIpAddressesDetection,
        hosting_provider_ip_restriction: BlockingPolicyModelHostingProviderIpRestriction,
        options: Optional[BlockingPolicyModelHostingProviderIpDetectionIsEnableOptions] = BlockingPolicyModelHostingProviderIpDetectionIsEnableOptions(),
    ) -> BlockingPolicyModel:
        return BlockingPolicyModel(
            pass_services,
            default_restriction,
            location_detection,
            anonymous_ip_detection,
            BlockingPolicyModelHostingProviderIpDetection.ENABLE,
            reputation_ip_detection,
            ip_addresses_detection,
            BlockingPolicyModelOptions(
                hosting_provider_ip_restriction,
                options.ip_addresses,
            ),
        )

    @staticmethod
    def hosting_provider_ip_detection_is_disable(
        pass_services: List[str],
        default_restriction: BlockingPolicyModelDefaultRestriction,
        location_detection: BlockingPolicyModelLocationDetection,
        anonymous_ip_detection: BlockingPolicyModelAnonymousIpDetection,
        reputation_ip_detection: BlockingPolicyModelReputationIpDetection,
        ip_addresses_detection: BlockingPolicyModelIpAddressesDetection,
        options: Optional[BlockingPolicyModelHostingProviderIpDetectionIsDisableOptions] = BlockingPolicyModelHostingProviderIpDetectionIsDisableOptions(),
    ) -> BlockingPolicyModel:
        return BlockingPolicyModel(
            pass_services,
            default_restriction,
            location_detection,
            anonymous_ip_detection,
            BlockingPolicyModelHostingProviderIpDetection.DISABLE,
            reputation_ip_detection,
            ip_addresses_detection,
            BlockingPolicyModelOptions(
                options.ip_addresses,
            ),
        )

    @staticmethod
    def reputation_ip_detection_is_enable(
        pass_services: List[str],
        default_restriction: BlockingPolicyModelDefaultRestriction,
        location_detection: BlockingPolicyModelLocationDetection,
        anonymous_ip_detection: BlockingPolicyModelAnonymousIpDetection,
        hosting_provider_ip_detection: BlockingPolicyModelHostingProviderIpDetection,
        ip_addresses_detection: BlockingPolicyModelIpAddressesDetection,
        reputation_ip_restriction: BlockingPolicyModelReputationIpRestriction,
        options: Optional[BlockingPolicyModelReputationIpDetectionIsEnableOptions] = BlockingPolicyModelReputationIpDetectionIsEnableOptions(),
    ) -> BlockingPolicyModel:
        return BlockingPolicyModel(
            pass_services,
            default_restriction,
            location_detection,
            anonymous_ip_detection,
            hosting_provider_ip_detection,
            BlockingPolicyModelReputationIpDetection.ENABLE,
            ip_addresses_detection,
            BlockingPolicyModelOptions(
                reputation_ip_restriction,
                options.ip_addresses,
            ),
        )

    @staticmethod
    def reputation_ip_detection_is_disable(
        pass_services: List[str],
        default_restriction: BlockingPolicyModelDefaultRestriction,
        location_detection: BlockingPolicyModelLocationDetection,
        anonymous_ip_detection: BlockingPolicyModelAnonymousIpDetection,
        hosting_provider_ip_detection: BlockingPolicyModelHostingProviderIpDetection,
        ip_addresses_detection: BlockingPolicyModelIpAddressesDetection,
        options: Optional[BlockingPolicyModelReputationIpDetectionIsDisableOptions] = BlockingPolicyModelReputationIpDetectionIsDisableOptions(),
    ) -> BlockingPolicyModel:
        return BlockingPolicyModel(
            pass_services,
            default_restriction,
            location_detection,
            anonymous_ip_detection,
            hosting_provider_ip_detection,
            BlockingPolicyModelReputationIpDetection.DISABLE,
            ip_addresses_detection,
            BlockingPolicyModelOptions(
                options.ip_addresses,
            ),
        )

    @staticmethod
    def ip_addresses_detection_is_enable(
        pass_services: List[str],
        default_restriction: BlockingPolicyModelDefaultRestriction,
        location_detection: BlockingPolicyModelLocationDetection,
        anonymous_ip_detection: BlockingPolicyModelAnonymousIpDetection,
        hosting_provider_ip_detection: BlockingPolicyModelHostingProviderIpDetection,
        reputation_ip_detection: BlockingPolicyModelReputationIpDetection,
        ip_address_restriction: BlockingPolicyModelIpAddressRestriction,
        options: Optional[BlockingPolicyModelIpAddressesDetectionIsEnableOptions] = BlockingPolicyModelIpAddressesDetectionIsEnableOptions(),
    ) -> BlockingPolicyModel:
        return BlockingPolicyModel(
            pass_services,
            default_restriction,
            location_detection,
            anonymous_ip_detection,
            hosting_provider_ip_detection,
            reputation_ip_detection,
            BlockingPolicyModelIpAddressesDetection.ENABLE,
            BlockingPolicyModelOptions(
                ip_address_restriction,
                options.ip_addresses,
            ),
        )

    @staticmethod
    def ip_addresses_detection_is_disable(
        pass_services: List[str],
        default_restriction: BlockingPolicyModelDefaultRestriction,
        location_detection: BlockingPolicyModelLocationDetection,
        anonymous_ip_detection: BlockingPolicyModelAnonymousIpDetection,
        hosting_provider_ip_detection: BlockingPolicyModelHostingProviderIpDetection,
        reputation_ip_detection: BlockingPolicyModelReputationIpDetection,
        options: Optional[BlockingPolicyModelIpAddressesDetectionIsDisableOptions] = BlockingPolicyModelIpAddressesDetectionIsDisableOptions(),
    ) -> BlockingPolicyModel:
        return BlockingPolicyModel(
            pass_services,
            default_restriction,
            location_detection,
            anonymous_ip_detection,
            hosting_provider_ip_detection,
            reputation_ip_detection,
            BlockingPolicyModelIpAddressesDetection.DISABLE,
            BlockingPolicyModelOptions(
                options.ip_addresses,
            ),
        )

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.pass_services is not None:
            properties["passServices"] = self.pass_services
        if self.default_restriction is not None:
            properties["defaultRestriction"] = self.default_restriction.value
        if self.location_detection is not None:
            properties["locationDetection"] = self.location_detection.value
        if self.locations is not None:
            properties["locations"] = self.locations
        if self.location_restriction is not None:
            properties["locationRestriction"] = self.location_restriction.value
        if self.anonymous_ip_detection is not None:
            properties["anonymousIpDetection"] = self.anonymous_ip_detection.value
        if self.anonymous_ip_restriction is not None:
            properties["anonymousIpRestriction"] = self.anonymous_ip_restriction.value
        if self.hosting_provider_ip_detection is not None:
            properties["hostingProviderIpDetection"] = self.hosting_provider_ip_detection.value
        if self.hosting_provider_ip_restriction is not None:
            properties["hostingProviderIpRestriction"] = self.hosting_provider_ip_restriction.value
        if self.reputation_ip_detection is not None:
            properties["reputationIpDetection"] = self.reputation_ip_detection.value
        if self.reputation_ip_restriction is not None:
            properties["reputationIpRestriction"] = self.reputation_ip_restriction.value
        if self.ip_addresses_detection is not None:
            properties["ipAddressesDetection"] = self.ip_addresses_detection.value
        if self.ip_addresses is not None:
            properties["ipAddresses"] = self.ip_addresses
        if self.ip_address_restriction is not None:
            properties["ipAddressRestriction"] = self.ip_address_restriction.value

        return properties
