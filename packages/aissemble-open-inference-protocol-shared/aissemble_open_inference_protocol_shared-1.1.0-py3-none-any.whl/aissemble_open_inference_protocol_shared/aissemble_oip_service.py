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

from aissemble_open_inference_protocol_shared.auth.auth_adapter_base import (
    AuthAdapterBase,
)
from aissemble_open_inference_protocol_shared.config.oip_config import OIPConfig
from aissemble_open_inference_protocol_shared.handlers.dataplane import (
    DataplaneHandler,
)
from aissemble_open_inference_protocol_shared.handlers.model_handler import (
    ModelHandler,
    DefaultModelHandler,
)


class AissembleOIPService(ABC):
    """
    Abstract class for all aiSSEMBLE Open Inference Protocol solutions. Defines required standardization.
    """

    def __init__(
        self,
        adapter: AuthAdapterBase | None,
        model_handler: ModelHandler = DefaultModelHandler(),
    ):
        super(AissembleOIPService, self).__init__()
        self.config = OIPConfig()
        self.model_handler = model_handler
        self.dataplane_handler = DataplaneHandler(self.model_handler)
        self.adapter = adapter
        self.server = None

    def model_load(self, model_name: str) -> bool:
        return self.model_handler.model_load(model_name)

    @abstractmethod
    async def start_server(self):
        pass
