###
# #%L
# aiSSEMBLE::Open Inference Protocol::Shared
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# #L%
###
from abc import ABC, abstractmethod
from krausening.logging import LogManager

import json
from typing import Optional


class AuthAdapterBase(ABC):
    """
    Check if the user is allowed to perform the action on the resource
    """

    logger = LogManager.get_instance().get_logger("AuthzAdapterBase")

    @abstractmethod
    def _authorize_impl(
        self,
        user: dict,
        resource: str,
        action: str,
        request_url: str,
        role: Optional[str] = None,
    ) -> bool:
        pass

    def authorize(
        self,
        user: dict,
        resource: str,
        action: str,
        user_ip: str,
        request_url: str,
        role: Optional[str] = None,
    ) -> bool:
        self.log_authorize(
            user=user,
            resource=resource,
            action=action,
            user_ip=user_ip,
            request_url=request_url,
            role=role,
        )

        pdp_decision = self._authorize_impl(
            user=user,
            resource=resource,
            action=action,
            request_url=request_url,
            role=role,
        )

        self.log_pdp_decision(user, pdp_decision)

        return pdp_decision

    def log_pdp_decision(self, user: str, pdp_decision):
        permit_or_deny = "PERMIT" if pdp_decision else "DENY"

        self.logger.info(f"PDP decision for user: {user}, was {permit_or_deny}")

    def log_authorize(
        self,
        user: dict,
        resource: str,
        action: str,
        user_ip: str,
        request_url: str,
        role: Optional[str] = None,
    ):
        authz_log_info = {
            "user": user,
            "resource": resource,
            "action": action,
            "role": role,
            "ip": user_ip,
            "request_url": request_url,
        }

        self.logger.info("Authorization start")

        self.logger.info("Auth request info:\n" + json.dumps(authz_log_info, indent=2))
