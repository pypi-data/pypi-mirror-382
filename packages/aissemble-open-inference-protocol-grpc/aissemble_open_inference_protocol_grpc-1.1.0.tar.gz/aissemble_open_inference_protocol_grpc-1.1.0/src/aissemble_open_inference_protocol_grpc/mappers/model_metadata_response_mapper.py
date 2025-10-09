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
from aissemble_open_inference_protocol_grpc.grpc_inference_service_pb2 import (
    ModelMetadataResponse,
)
from aissemble_open_inference_protocol_shared.types.dataplane import (
    ModelMetadataResponse as ModelMetadataResponseType,
    MetadataTensor,
)


class ModelMetadataResponseMapper:
    """
    Class used to map handler model metadata response to the gRPC model metadata response.
    """

    @staticmethod
    def from_model_metadata_response(
        response: ModelMetadataResponseType,
    ) -> ModelMetadataResponse:
        """
        Maps the handlers model metadata response to the gRPC equivalent
        Args:
            response: The handlers model metadata response

        Returns: the gRPC equivalent model metadata response
        """
        return ModelMetadataResponse(
            name=response.name,
            versions=response.versions,
            platform=response.platform,
            inputs=[
                ModelMetadataResponseMapper.from_metadata_tensor(inputs)
                for inputs in response.inputs
            ],
            outputs=[
                ModelMetadataResponseMapper.from_metadata_tensor(outputs)
                for outputs in response.outputs
            ],
        )

    @staticmethod
    def from_metadata_tensor(
        metadata_tensor: MetadataTensor,
    ) -> ModelMetadataResponse.TensorMetadata:
        return ModelMetadataResponse.TensorMetadata(
            name=metadata_tensor.name,
            datatype=metadata_tensor.datatype.value,
            shape=metadata_tensor.shape,
        )
