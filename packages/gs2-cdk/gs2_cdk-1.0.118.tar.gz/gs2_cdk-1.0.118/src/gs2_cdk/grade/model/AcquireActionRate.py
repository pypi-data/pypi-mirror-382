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
from .options.AcquireActionRateOptions import AcquireActionRateOptions
from .options.AcquireActionRateModeIsDoubleOptions import AcquireActionRateModeIsDoubleOptions
from .options.AcquireActionRateModeIsBigOptions import AcquireActionRateModeIsBigOptions
from .enums.AcquireActionRateMode import AcquireActionRateMode


class AcquireActionRate:
    name: str
    mode: AcquireActionRateMode
    rates: Optional[List[float]] = None
    big_rates: Optional[List[str]] = None

    def __init__(
        self,
        name: str,
        mode: AcquireActionRateMode,
        options: Optional[AcquireActionRateOptions] = AcquireActionRateOptions(),
    ):
        self.name = name
        self.mode = mode
        self.rates = options.rates if options.rates else None
        self.big_rates = options.big_rates if options.big_rates else None

    @staticmethod
    def mode_is_double(
        name: str,
        rates: List[float],
        options: Optional[AcquireActionRateModeIsDoubleOptions] = AcquireActionRateModeIsDoubleOptions(),
    ) -> AcquireActionRate:
        return AcquireActionRate(
            name,
            AcquireActionRateMode.DOUBLE,
            AcquireActionRateOptions(
                rates,
            ),
        )

    @staticmethod
    def mode_is_big(
        name: str,
        big_rates: List[str],
        options: Optional[AcquireActionRateModeIsBigOptions] = AcquireActionRateModeIsBigOptions(),
    ) -> AcquireActionRate:
        return AcquireActionRate(
            name,
            AcquireActionRateMode.BIG,
            AcquireActionRateOptions(
                big_rates,
            ),
        )

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.mode is not None:
            properties["mode"] = self.mode.value
        if self.rates is not None:
            properties["rates"] = self.rates
        if self.big_rates is not None:
            properties["bigRates"] = self.big_rates

        return properties
