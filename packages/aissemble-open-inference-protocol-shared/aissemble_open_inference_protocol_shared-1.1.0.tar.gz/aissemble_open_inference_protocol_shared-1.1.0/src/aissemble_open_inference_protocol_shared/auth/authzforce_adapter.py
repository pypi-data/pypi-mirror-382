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
import requests
from .auth_adapter_base import AuthAdapterBase
from aissemble_open_inference_protocol_shared.auth.xacml3_builder import (
    XacmlRequestBuilder,
)
from ..config.oip_config import OIPConfig

from typing import Optional


class AuthzforceAdapter(AuthAdapterBase):
    def __init__(self):
        self.config = OIPConfig()
        self.pdp_url = self.config.pdp_url()

    def _authorize_impl(
        self,
        user: str,
        resource: str,
        action: str,
        request_url: str,
        role: Optional[str] = None,
    ) -> bool:
        """
        This method composes a XACML 3.0 request using the provided parameters and sends
        an authorization request to the Authzforce server.  The Authzforce pdp url is
        specified in the oip.properties file (http://localhost:8080/pdp by default)
        :param user: The name of the subject/user
        :param resource: The resource being requested
        :param action: The action being requested
        :param role: The role associated with the user/subject
        :return: returns PERMIT if the PDP policy matched the request.  Deny otherwise.
        """
        xacml_request_builder = XacmlRequestBuilder()

        # The following code for role should be revisited in a follow on ticket to
        # replace with ABAC.  All attributes should be added to the XACML request.
        if role:
            if isinstance(role, list):
                role = role[0]

        payload = xacml_request_builder.build_request(
            user=user, role=role, resource=resource, action=action
        )

        headers = {"Content-Type": "application/xacml+json"}
        response = requests.post(self.pdp_url, headers=headers, data=payload)

        return response.json().get("Response", [{}])[0].get("Decision") == "Permit"
