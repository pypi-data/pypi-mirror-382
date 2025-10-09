###
# #%L
# aiSSEMBLE::Open Inference Protocol::gRPC
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
import asyncio
import signal
from concurrent.futures import ThreadPoolExecutor

from grpc import aio
from krausening.logging import LogManager

from aissemble_open_inference_protocol_grpc.auth.auth_interceptor import AuthInterceptor
from aissemble_open_inference_protocol_grpc.grpc_inference_service_pb2_grpc import (
    add_GrpcInferenceServiceServicer_to_server,
)
from aissemble_open_inference_protocol_grpc.inference_servicer import InferenceServicer
from aissemble_open_inference_protocol_shared.aissemble_oip_service import (
    AissembleOIPService,
)
from aissemble_open_inference_protocol_shared.auth.auth_adapter_base import (
    AuthAdapterBase,
)
from aissemble_open_inference_protocol_shared.auth.default_adapter import DefaultAdapter
from aissemble_open_inference_protocol_shared.handlers.model_handler import (
    ModelHandler,
    DefaultModelHandler,
)


class AissembleOIPgRPC(AissembleOIPService):
    logger = LogManager.get_instance().get_logger("AissembleOIPgRPC")

    def __init__(
        self,
        model_handler: ModelHandler = DefaultModelHandler(),
        adapter: AuthAdapterBase = DefaultAdapter(),
    ):
        super().__init__(adapter, model_handler)
        self.server = self.create_server()

    async def start_server(self):
        # Add signal handlers to shut down gracefully
        self._add_terminate_signal_handlers()

        # Create server if not already created
        if not self.server:
            self.create_server()
        self.logger.info("Starting OIP gRPC Server")

        await self.server.start()
        self.logger.info(
            f"gRPC server started at grpc://{self.config.grpc_host}:{self.config.grpc_port}"
        )
        if self.config.auth_enabled:
            self.logger.info("Authorization is enabled")
        else:
            self.logger.info("Authorization is disabled")
        await self.server.wait_for_termination()

    def create_server(self):
        inference_servicer = InferenceServicer(self.dataplane_handler)
        self.server = aio.server(
            ThreadPoolExecutor(max_workers=self.config.grpc_workers),
            interceptors=self._get_interceptors(),
        )
        add_GrpcInferenceServiceServicer_to_server(inference_servicer, self.server)
        self.server.add_insecure_port(
            f"{self.config.grpc_host}:{self.config.grpc_port}"
        )
        return self.server

    def _add_terminate_signal_handlers(self):
        self.logger.info("Adding terminate signal handlers")
        loop = asyncio.get_running_loop()

        for sig in signal.SIGINT, signal.SIGTERM, signal.SIGQUIT:
            loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(self.stop()))

    def _get_interceptors(self):
        interceptors = []
        if self.config.auth_enabled:
            interceptors.append(AuthInterceptor(auth_adapter=self.adapter))
        return interceptors

    async def stop(self):
        self.logger.info("Stopping OIP GRPC Server")
        await self.server.stop(grace=10)
