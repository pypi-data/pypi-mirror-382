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
import argparse


def strtobool(val: str) -> bool:
    """Convert a string representation of truth to True or False.

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.

    Copied from KServe's utils.strtobool function, which was originally
    adapted from deprecated `distutils`
    https://github.com/python/cpython/blob/3.11/Lib/distutils/util.py
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))


class KServeArgsParser:
    @staticmethod
    def parse_kserve_args() -> dict[str, int | bool | str]:
        """
        Parse Kserve ModelServer standard arguments.

        Returns:
            dict[str, int | bool | str]: A dictionary containing only the arguments that were
            explicitly provided (filters out None/unset values).
        """

        parser = argparse.ArgumentParser(
            description="KServe ModelServer configuration", add_help=False
        )

        # KServe ModelServer arguments
        parser.add_argument(
            "--http_port",
            type=int,
            help="The HTTP Port listened to by the model server.",
        )
        parser.add_argument(
            "--grpc_port",
            type=int,
            help="The gRPC Port listened to by the model server.",
        )
        parser.add_argument(
            "--workers",
            type=int,
            help="Number of uvicorn workers for multiprocessing.",
        )
        parser.add_argument(
            "--max_threads",
            type=int,
            help="Max number of gRPC processing threads.",
        )
        parser.add_argument(
            "--max_asyncio_workers",
            type=int,
            help="Max number of AsyncIO threads.",
        )
        parser.add_argument(
            "--enable_grpc",
            type=strtobool,
            help="Whether to enable gRPC for the model server.",
        )
        parser.add_argument(
            "--enable_docs_url",
            type=strtobool,
            help="Whether to enable docs url '/docs' to display Swagger UI.",
        )
        parser.add_argument(
            "--enable_latency_logging",
            type=strtobool,
            help="Whether to enable latency logging for requests.",
        )
        parser.add_argument(
            "--access_log_format",
            type=str,
            help="Format to set for the access log (provided by asgi-logger).",
        )

        parsed_args, _ = parser.parse_known_args()
        return {
            key: value for key, value in vars(parsed_args).items() if value is not None
        }
