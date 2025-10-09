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
from typing import Optional

from aissemble_open_inference_protocol_shared.types.dataplane import (
    InferenceRequest,
    InferenceResponse,
    ModelMetadataResponse,
    ModelReadyResponse,
)


class ModelHandler(ABC):
    @abstractmethod
    def infer(
        self,
        payload: InferenceRequest,
        model_name: str,
        model_version: Optional[str] = None,
    ) -> InferenceResponse:
        """
        Perform inference on the given inference request.

        Args:
            payload: The request to perform inference against.
            model_name: The model to perform inference against.
            model_version: The model version

        Returns:
            Results of the inference.
        """
        pass

    @abstractmethod
    def model_metadata(
        self,
        model_name: str,
        model_version: Optional[str] = None,
    ) -> ModelMetadataResponse:
        """
        Get metadata for a given model.

        Args:
            model_name: Name of the model.
            model_version: Version of the model.

        Returns:
            The metadata for the given model.
        """
        pass

    @abstractmethod
    def model_load(self, model_name: str) -> bool:
        """
        Loads the given model.

        Args:
            model_name: Name of the model to load.

        Returns:
            True if the model was successfully loaded, False otherwise.
        """
        pass

    def model_ready(
        self,
        model_name: str,
        model_version: Optional[str] = None,
    ) -> ModelReadyResponse:
        """
        Call to determine if the model is ready.

        Args:
            model_name: The model name.
            model_version: The model version.

        Returns:
            ModelReadyResponse for the given model.
        """
        return ModelReadyResponse(name=model_name, ready=True)


class DefaultModelHandler(ModelHandler):
    def infer(
        self,
        payload: InferenceRequest,
        model_name: str,
        model_version: Optional[str] = None,
    ) -> InferenceResponse:
        raise NotImplementedError

    def model_metadata(
        self,
        model_name: str,
        model_version: Optional[str] = None,
    ) -> ModelMetadataResponse:
        raise NotImplementedError

    def model_load(self, model_name: str) -> bool:
        raise NotImplementedError
