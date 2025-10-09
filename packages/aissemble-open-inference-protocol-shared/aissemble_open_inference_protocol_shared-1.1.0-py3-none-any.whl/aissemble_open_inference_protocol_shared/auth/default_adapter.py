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
from .auth_adapter_base import AuthAdapterBase
from typing import Optional


class DefaultAdapter(AuthAdapterBase):
    def __init__(self):
        # This is just an example property that is not actually used.
        # A full implementation will make use of a service url.
        self.service_url = "http://localhost:<some port>/<some path>"

    def _authorize_impl(
        self,
        user: dict,
        resource: str,
        action: str,
        request_url: str,
        role: Optional[str] = None,
    ) -> bool:
        return True
