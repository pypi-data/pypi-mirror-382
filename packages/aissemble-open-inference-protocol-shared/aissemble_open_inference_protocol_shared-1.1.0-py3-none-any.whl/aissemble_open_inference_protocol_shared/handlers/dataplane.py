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
from typing import Optional

from aissemble_open_inference_protocol_shared.handlers.model_handler import (
    ModelHandler,
    DefaultModelHandler,
)
from aissemble_open_inference_protocol_shared.types.dataplane import (
    InferenceRequest,
    InferenceResponse,
    ModelMetadataResponse,
    ModelReadyResponse,
    ServerReadyResponse,
    ServerLiveResponse,
    ServerMetadataResponse,
)


class DataplaneHandler:
    def __init__(self, model_handler: ModelHandler = DefaultModelHandler()):
        self.model_handler = model_handler

    def infer(
        self,
        payload: InferenceRequest,
        model_name: str,
        model_version: Optional[str] = None,
    ) -> InferenceResponse:
        # TODO we need to move the codec logic calls here so it is not one solution specific

        # Validate request
        payload.validate_oip()

        infer_response = self.model_handler.infer(payload, model_name, model_version)

        # Validate response
        infer_response.validate_oip()
        return infer_response

    def model_metadata(
        self,
        model_name: str,
        model_version: Optional[str] = None,
    ) -> ModelMetadataResponse:
        return self.model_handler.model_metadata(model_name, model_version)

    def model_load(self, model_name: str) -> bool:
        return self.model_handler.model_load(model_name)

    def model_ready(
        self,
        model_name: str,
        model_version: Optional[str] = None,
    ) -> ModelReadyResponse:
        return self.model_handler.model_ready(model_name, model_version)

    def server_ready(self) -> ServerReadyResponse:
        return ServerReadyResponse(live=True)

    def server_live(self) -> ServerLiveResponse:
        return ServerLiveResponse(live=True)

    def server_metadata(self) -> ServerMetadataResponse:
        return ServerMetadataResponse(
            name="Inference Server", version="1.0", extensions=[]
        )
