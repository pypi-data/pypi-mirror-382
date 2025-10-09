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

###
# Acknowledgment:
# This implementation is inspired by the MLServer project.
# It follows similar design principles to integrate with the aissemble-open-inference-protocol.
# See MLServer’s license for details:
# Apache License Version 2.0 (https://github.com/SeldonIO/MLServer/blob/master/LICENSE)
###

from typing import Any, ClassVar, Type, Union, Optional

from aissemble_open_inference_protocol_shared.types.dataplane import (
    RequestInput,
    ResponseOutput,
    InferenceRequest,
    InferenceResponse,
)
from krausening.logging import LogManager

logger = LogManager.get_instance().get_logger("Codec")

InputCodecType = Union[Type["InputCodec"], "InputCodec"]
RequestCodecType = Union[Type["RequestCodec"], "RequestCodec"]


class InputCodec:
    ContentType: ClassVar[str] = ""

    @classmethod
    def can_encode(cls, payload: Any) -> bool:
        """Return True if this codec can encode/decode the given payload."""
        return False

    @classmethod
    def encode_input(cls, name: str, payload: Any, **kwargs) -> RequestInput:
        """Encode Python payload into a RequestInput."""
        raise NotImplementedError()

    @classmethod
    def decode_input(cls, request_input: RequestInput) -> Any:
        """Decode RequestInput into Python payload."""
        raise NotImplementedError()

    @classmethod
    def encode_output(cls, name: str, payload: Any, **kwargs) -> ResponseOutput:
        """Encode Python payload into a ResponseOutput."""
        raise NotImplementedError()

    @classmethod
    def decode_output(cls, response_output: ResponseOutput) -> Any:
        """Decode ResponseOutput into Python payload."""
        raise NotImplementedError()


class RequestCodec:
    ContentType: ClassVar[str] = ""

    @classmethod
    def can_encode(cls, payload: Any) -> bool:
        """Return True if this codec can encode/decode the given payload."""
        return False

    @classmethod
    def encode_request(cls, payload: Any, **kwargs) -> InferenceRequest:
        """Encode Python payload into an InferenceRequest."""
        raise NotImplementedError()

    @classmethod
    def decode_request(cls, request: InferenceRequest) -> Any:
        """Decode InferenceRequest into Python payload."""
        raise NotImplementedError()

    @classmethod
    def encode_response(
        cls,
        model_name: str,
        payload: Any,
        model_version: Optional[str] = None,
        **kwargs,
    ) -> InferenceResponse:
        """Encode Python payload into an InferenceResponse."""
        raise NotImplementedError()

    @classmethod
    def decode_response(cls, response: InferenceResponse) -> Any:
        """Decode InferenceResponse into Python payload."""
        raise NotImplementedError()
