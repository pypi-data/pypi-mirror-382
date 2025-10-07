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

from ...core.func import GetAttr, Join
from .StaminaModelRef import StaminaModelRef
from ..stamp_sheet.RecoverStaminaByUserId import RecoverStaminaByUserId
from ..stamp_sheet.RaiseMaxValueByUserId import RaiseMaxValueByUserId
from ..stamp_sheet.SetMaxValueByUserId import SetMaxValueByUserId
from ..stamp_sheet.SetRecoverIntervalByUserId import SetRecoverIntervalByUserId
from ..stamp_sheet.SetRecoverValueByUserId import SetRecoverValueByUserId
from ..stamp_sheet.DecreaseMaxValueByUserId import DecreaseMaxValueByUserId
from ..stamp_sheet.ConsumeStaminaByUserId import ConsumeStaminaByUserId
from ..stamp_sheet.VerifyStaminaValueByUserId import VerifyStaminaValueByUserId
from ..stamp_sheet.VerifyStaminaMaxValueByUserId import VerifyStaminaMaxValueByUserId
from ..stamp_sheet.VerifyStaminaRecoverIntervalMinutesByUserId import VerifyStaminaRecoverIntervalMinutesByUserId
from ..stamp_sheet.VerifyStaminaRecoverValueByUserId import VerifyStaminaRecoverValueByUserId
from ..stamp_sheet.VerifyStaminaOverflowValueByUserId import VerifyStaminaOverflowValueByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def stamina_model(
        self,
        stamina_name: str,
    ) -> StaminaModelRef:
        return StaminaModelRef(
            self.namespace_name,
            stamina_name,
        )

    def recover_stamina(
        self,
        stamina_name: str,
        recover_value: int,
        user_id: Optional[str] = "#{userId}",
    ) -> RecoverStaminaByUserId:
        return RecoverStaminaByUserId(
            self.namespace_name,
            stamina_name,
            recover_value,
            user_id,
        )

    def raise_max_value(
        self,
        stamina_name: str,
        raise_value: int,
        user_id: Optional[str] = "#{userId}",
    ) -> RaiseMaxValueByUserId:
        return RaiseMaxValueByUserId(
            self.namespace_name,
            stamina_name,
            raise_value,
            user_id,
        )

    def set_max_value(
        self,
        stamina_name: str,
        max_value: int,
        user_id: Optional[str] = "#{userId}",
    ) -> SetMaxValueByUserId:
        return SetMaxValueByUserId(
            self.namespace_name,
            stamina_name,
            max_value,
            user_id,
        )

    def set_recover_interval(
        self,
        stamina_name: str,
        recover_interval_minutes: int,
        user_id: Optional[str] = "#{userId}",
    ) -> SetRecoverIntervalByUserId:
        return SetRecoverIntervalByUserId(
            self.namespace_name,
            stamina_name,
            recover_interval_minutes,
            user_id,
        )

    def set_recover_value(
        self,
        stamina_name: str,
        recover_value: int,
        user_id: Optional[str] = "#{userId}",
    ) -> SetRecoverValueByUserId:
        return SetRecoverValueByUserId(
            self.namespace_name,
            stamina_name,
            recover_value,
            user_id,
        )

    def decrease_max_value(
        self,
        stamina_name: str,
        decrease_value: int,
        user_id: Optional[str] = "#{userId}",
    ) -> DecreaseMaxValueByUserId:
        return DecreaseMaxValueByUserId(
            self.namespace_name,
            stamina_name,
            decrease_value,
            user_id,
        )

    def consume_stamina(
        self,
        stamina_name: str,
        consume_value: int,
        user_id: Optional[str] = "#{userId}",
    ) -> ConsumeStaminaByUserId:
        return ConsumeStaminaByUserId(
            self.namespace_name,
            stamina_name,
            consume_value,
            user_id,
        )

    def verify_stamina_value(
        self,
        stamina_name: str,
        verify_type: str,
        value: int,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyStaminaValueByUserId:
        return VerifyStaminaValueByUserId(
            self.namespace_name,
            stamina_name,
            verify_type,
            value,
            multiply_value_specifying_quantity,
            user_id,
        )

    def verify_stamina_max_value(
        self,
        stamina_name: str,
        verify_type: str,
        value: int,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyStaminaMaxValueByUserId:
        return VerifyStaminaMaxValueByUserId(
            self.namespace_name,
            stamina_name,
            verify_type,
            value,
            multiply_value_specifying_quantity,
            user_id,
        )

    def verify_stamina_recover_interval_minutes(
        self,
        stamina_name: str,
        verify_type: str,
        value: int,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyStaminaRecoverIntervalMinutesByUserId:
        return VerifyStaminaRecoverIntervalMinutesByUserId(
            self.namespace_name,
            stamina_name,
            verify_type,
            value,
            multiply_value_specifying_quantity,
            user_id,
        )

    def verify_stamina_recover_value(
        self,
        stamina_name: str,
        verify_type: str,
        value: int,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyStaminaRecoverValueByUserId:
        return VerifyStaminaRecoverValueByUserId(
            self.namespace_name,
            stamina_name,
            verify_type,
            value,
            multiply_value_specifying_quantity,
            user_id,
        )

    def verify_stamina_overflow_value(
        self,
        stamina_name: str,
        verify_type: str,
        value: int,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyStaminaOverflowValueByUserId:
        return VerifyStaminaOverflowValueByUserId(
            self.namespace_name,
            stamina_name,
            verify_type,
            value,
            multiply_value_specifying_quantity,
            user_id,
        )

    def grn(
        self,
    ) -> str:
        return Join(
            ":",
            [
                "grn",
                "gs2",
                GetAttr.region(
                ).str(
                ),
                GetAttr.owner_id(
                ).str(
                ),
                "stamina",
                self.namespace_name,
            ],
        ).str(
        )
