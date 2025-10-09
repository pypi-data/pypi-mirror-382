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
import os
from typing import Optional, Union

from krausening.properties import PropertyManager

from aissemble_open_inference_protocol_shared.config.kserve_args_parser import (
    KServeArgsParser,
)


class OIPConfig:
    """
    Configurations for OIP
    """

    DEFAULT_ALGORITHM = "HS256"
    DEFAULT_PDP_URL = "http://localhost:8080/pdp"

    DEFAULT_GRPC_HOST = "0.0.0.0"
    DEFAULT_GRPC_PORT = "8081"
    DEFAULT_GRPC_WORKERS = "3"
    DEFAULT_AUTH_ENABLED = "true"

    DEFAULT_FASTAPI_HOST = "127.0.0.1"
    DEFAULT_FASTAPI_PORT = "8082"
    DEFAULT_FASTAPI_RELOAD = "True"

    DEFAULT_KSERVE_HTTP_PORT = "8080"
    DEFAULT_KSERVE_GRPC_PORT = "8081"
    DEFAULT_KSERVE_WORKERS = "1"
    DEFAULT_KSERVE_MAX_THREADS = "4"
    DEFAULT_KSERVE_MAX_ASYNCIO_WORKERS = ""  # Represents None
    DEFAULT_KSERVE_ENABLE_GRPC = "True"
    DEFAULT_KSERVE_ENABLE_DOCS_URL = "False"
    DEFAULT_KSERVE_ENABLE_LATENCY_LOGGING = "True"
    DEFAULT_KSERVE_ACCESS_LOG_FORMAT = ""  # Represents None

    def __init__(self):
        self.properties = PropertyManager.get_instance().get_properties(
            "oip.properties"
        )
        self._parsed_args = KServeArgsParser.parse_kserve_args()

    #########################
    # Authorization
    #########################

    @property
    def auth_enabled(self) -> bool:
        """
        Whether authorization is enabled for the server.
        If auth_enabled is set to true with no protected endpoints specified then all endpoints are protected.
        """
        value = self.properties.getProperty("auth_enabled", self.DEFAULT_AUTH_ENABLED)
        environ_override = os.getenv("AUTH_ENABLED")
        enabled = environ_override if environ_override else value
        return str(enabled).lower() == "true"

    def auth_secret(self):
        """
        Returns the auth secret key
        """
        value = self.properties.getProperty("auth_secret", "")
        environ_override = os.getenv("AUTH_SECRET")
        return environ_override if environ_override else value

    def auth_algorithm(self):
        """
        Returns the auth algorithm
        """
        value = self.properties.getProperty("auth_algorithm", self.DEFAULT_ALGORITHM)
        environ_override = os.getenv("AUTH_ALGORITHM")
        return environ_override if environ_override else value

    def pdp_url(self):
        """
        Returns the PDP url
        """
        value = self.properties.getProperty("pdp_url", self.DEFAULT_PDP_URL)
        environ_override = os.getenv("OIP_PDP_URL")
        return environ_override if environ_override else value

    #########################
    # gRPC
    #########################
    @property
    def grpc_host(self) -> str:
        value = self.properties.getProperty("grpc_host", self.DEFAULT_GRPC_HOST)
        environ_override = os.getenv("GRPC_HOST")
        return environ_override if environ_override else value

    @property
    def grpc_port(self) -> str:
        value = self.properties.getProperty("grpc_port", self.DEFAULT_GRPC_PORT)
        environ_override = os.getenv("GRPC_PORT")
        return environ_override if environ_override else value

    @property
    def grpc_workers(self) -> int:
        value = self.properties.getProperty("grpc_workers", self.DEFAULT_GRPC_WORKERS)
        environ_override = os.getenv("GRPC_WORKERS")
        worker_count = environ_override if environ_override else value
        return int(worker_count)

    #########################
    # FastAPI
    #########################
    # , reload=reload, host=host, port=port
    @property
    def fastapi_host(self) -> str:
        value = self.properties.getProperty("fastapi_host", self.DEFAULT_FASTAPI_HOST)
        environ_override = os.getenv("FASTAPI_HOST")
        return environ_override if environ_override else value

    @property
    def fastapi_port(self) -> int:
        value = self.properties.getProperty("fastapi_port", self.DEFAULT_FASTAPI_PORT)
        environ_override = os.getenv("FASTAPI_PORT")
        return int(environ_override if environ_override else value)

    @property
    def fastapi_reload(self) -> bool:
        value = self.properties.getProperty(
            "fastapi_reload", self.DEFAULT_FASTAPI_RELOAD
        )
        environ_override = os.getenv("FASTAPI_RELOAD")
        return bool(environ_override if environ_override else value)

    #########################
    # Kserve
    #########################

    def _get_config_value(
        self,
        arg_key: str,
        env_key: str,
        prop_key: str,
        default_value: str,
        target_type: type,
    ) -> Union[str, int, bool, None]:
        """
        Get configuration value following precedence: args > env > properties > default value

        Args:
            arg_key: Key in parsed arguments dict
            env_key: Environment variable name
            prop_key: Krausening property name
            default_value: Default value as string
            target_type: Type to convert string values to
        """

        # Check args
        if arg_key in self._parsed_args:
            return self._parsed_args[arg_key]

        # Check Environment variables. If None, check properties.
        value = os.getenv(env_key)
        if value is None:
            value = self.properties.getProperty(prop_key, default_value)

        if value == "" and default_value == "":
            return None

        if target_type is bool:
            return value.lower() == "true"
        elif target_type is int:
            try:
                return int(value)
            except ValueError as e:
                raise ValueError(f"Invalid integer value '{value}': {e}")
        elif target_type is str:
            return value
        else:
            raise ValueError(f"Unsupported conversion type: {target_type}")

    @property
    def kserve_http_port(self) -> int:
        """
        The HTTP Port listened to by the model server.
        """
        return self._get_config_value(
            arg_key="http_port",
            env_key="KSERVE_HTTP_PORT",
            prop_key="kserve_http_port",
            default_value=self.DEFAULT_KSERVE_HTTP_PORT,
            target_type=int,
        )

    @property
    def kserve_grpc_port(self) -> int:
        """
        The gRPC Port listened to by the model server.
        """
        return self._get_config_value(
            arg_key="grpc_port",
            env_key="KSERVE_GRPC_PORT",
            prop_key="kserve_grpc_port",
            default_value=self.DEFAULT_KSERVE_GRPC_PORT,
            target_type=int,
        )

    @property
    def kserve_workers(self) -> int:
        """
        Number of uvicorn workers for multiprocessing.
        """
        return self._get_config_value(
            arg_key="workers",
            env_key="KSERVE_WORKERS",
            prop_key="kserve_workers",
            default_value=self.DEFAULT_KSERVE_WORKERS,
            target_type=int,
        )

    @property
    def kserve_max_threads(self) -> int:
        """
        Max number of gRPC processing threads.
        """
        return self._get_config_value(
            arg_key="max_threads",
            env_key="KSERVE_MAX_THREADS",
            prop_key="kserve_max_threads",
            default_value=self.DEFAULT_KSERVE_MAX_THREADS,
            target_type=int,
        )

    @property
    def kserve_max_asyncio_workers(self) -> Optional[int]:
        """
        Max number of AsyncIO threads. Default returns `None`.
        """
        return self._get_config_value(
            arg_key="max_asyncio_workers",
            env_key="KSERVE_MAX_ASYNCIO_WORKERS",
            prop_key="kserve_max_asyncio_workers",
            default_value=self.DEFAULT_KSERVE_MAX_ASYNCIO_WORKERS,
            target_type=int,
        )

    @property
    def kserve_enable_grpc(self) -> bool:
        """
        Whether to enable gRPC for the model server.
        """
        return self._get_config_value(
            arg_key="enable_grpc",
            env_key="KSERVE_ENABLE_GRPC",
            prop_key="kserve_enable_grpc",
            default_value=self.DEFAULT_KSERVE_ENABLE_GRPC,
            target_type=bool,
        )

    @property
    def kserve_enable_docs_url(self) -> bool:
        """
        Whether to enable docs url '/docs' to display Swagger UI.
        """
        return self._get_config_value(
            arg_key="enable_docs_url",
            env_key="KSERVE_ENABLE_DOCS_URL",
            prop_key="kserve_enable_docs_url",
            default_value=self.DEFAULT_KSERVE_ENABLE_DOCS_URL,
            target_type=bool,
        )

    @property
    def kserve_enable_latency_logging(self) -> bool:
        """
        Whether to enable latency logging for requests.
        """
        return self._get_config_value(
            arg_key="enable_latency_logging",
            env_key="KSERVE_ENABLE_LATENCY_LOGGING",
            prop_key="kserve_enable_latency_logging",
            default_value=self.DEFAULT_KSERVE_ENABLE_LATENCY_LOGGING,
            target_type=bool,
        )

    @property
    def kserve_access_log_format(self) -> Optional[str]:
        """
        Format to set for the access log (provided by asgi-logger). Default returns `None`.
        """
        return self._get_config_value(
            arg_key="access_log_format",
            env_key="KSERVE_ACCESS_LOG_FORMAT",
            prop_key="kserve_access_log_format",
            default_value=self.DEFAULT_KSERVE_ACCESS_LOG_FORMAT,
            target_type=str,
        )
