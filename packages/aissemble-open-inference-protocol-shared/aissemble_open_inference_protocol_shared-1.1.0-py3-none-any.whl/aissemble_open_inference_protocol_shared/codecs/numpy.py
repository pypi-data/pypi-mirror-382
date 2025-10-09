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
#
# Inspired by MLServer project, see MLServer’s license for details:
# Apache License, Version 2.0 (https://github.com/SeldonIO/MLServer/blob/master/LICENSE)

import numpy as np
from typing import Any
from aissemble_open_inference_protocol_shared.codecs.codec import InputCodec
from aissemble_open_inference_protocol_shared.codecs.registry import (
    register_input_codec,
    register_request_codec,
)
from aissemble_open_inference_protocol_shared.codecs.utils import (
    InputOrOutput,
    SingleTensorRequestCodec,
)
from aissemble_open_inference_protocol_shared.types.dataplane import (
    Parameters,
    RequestInput,
    ResponseOutput,
)
from krausening.logging import LogManager

logger = LogManager.get_instance().get_logger("NumpyArrayCodec")

PROTOCOL_TO_NUMPY = {
    "BOOL": np.bool_,
    "INT8": np.int8,
    "INT16": np.int16,
    "INT32": np.int32,
    "INT64": np.int64,
    "UINT8": np.uint8,
    "UINT16": np.uint16,
    "UINT32": np.uint32,
    "UINT64": np.uint64,
    "FP16": np.float16,
    "FP32": np.float32,
    "FP64": np.float64,
}


# Helper to infer protocol datatype from numpy dtype
def infer_protocol_datatype(arr: np.ndarray) -> str:
    """
    Check for match in PROTOCOL_TO_NUMPY, default to BYTES if no match
    """
    for proto, dtype in PROTOCOL_TO_NUMPY.items():
        if arr.dtype == dtype:
            return proto
    return "BYTES"


def to_numpy_array(arr: Any, dtype: np.dtype = None) -> np.ndarray:
    """
    Convert to numpy array if not already one with appropriate dtype
    """
    if isinstance(arr, np.ndarray):
        return arr
    return np.array(arr, dtype=dtype)


def decode_input_or_output(input_or_output: InputOrOutput) -> np.ndarray:
    """
    Decode the data from RequestInput or ResponseOutput into a numpy array
    Also determines the appropriate numpy dtype based on the protocol datatype
    """
    raw_data = input_or_output.data.root
    protocol_datatype = getattr(input_or_output, "datatype", None)
    dtype = PROTOCOL_TO_NUMPY.get(protocol_datatype, None)
    return to_numpy_array(raw_data, dtype=dtype)


def encode_payload(payload: Any):
    """
    Convert payload to numpy array and extract datatype, shape, and data for encoding.
    """
    arr = to_numpy_array(payload)
    shape = list(arr.shape)
    if arr.ndim == 1:
        shape = [1, arr.shape[0]]
    data = arr.tolist()
    datatype = infer_protocol_datatype(arr)
    return datatype, shape, data


# Decorator adds NumpyArrayCodec to the global input-codec registry under "numpy"
@register_input_codec
class NumpyArrayCodec(InputCodec):
    ContentType = "numpy"

    @classmethod
    def can_encode(cls, payload: Any) -> bool:
        """
        Return True if numpy codec can handle the given payload.
        """
        try:
            arr = to_numpy_array(payload)
            return arr.ndim >= 1
        except Exception:
            return False

    @classmethod
    def encode_input(cls, name: str, payload: Any, **kwargs) -> RequestInput:
        """
        Encode a Python array into a RequestInput.
        """
        datatype, shape, data = encode_payload(payload=payload)
        return RequestInput(
            name=name,
            datatype=datatype,
            shape=shape,
            data=data,
            parameters=Parameters(content_type=cls.ContentType),
        )

    @classmethod
    def encode_output(cls, name: str, payload: Any, **kwargs) -> ResponseOutput:
        """
        Encode a Python array into a ResponseOutput.
        """
        datatype, shape, data = encode_payload(payload=payload)
        return ResponseOutput(
            name=name,
            datatype=datatype,
            shape=shape,
            data=data,
            parameters=Parameters(content_type=cls.ContentType),
        )

    @classmethod
    def decode_input(cls, request_input: RequestInput) -> np.ndarray:
        """
        Decode a RequestInput back into a numpy array.
        """
        return decode_input_or_output(request_input)

    @classmethod
    def decode_output(cls, response_output: ResponseOutput) -> np.ndarray:
        """
        Decode a ResponseOutput back into a numpy array.
        """
        return decode_input_or_output(response_output)


@register_request_codec
class NumpyArrayRequestCodec(SingleTensorRequestCodec):
    """
    Wraps NumpyArrayCodec into a full InferenceRequest/Response by decoding
    the first input/output tensor as a numpy array and re-encoding it on output.
    """

    InputCodec = NumpyArrayCodec
    ContentType = NumpyArrayCodec.ContentType


# %%
