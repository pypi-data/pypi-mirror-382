# aiSSEMBLE&trade; Open Inference Protocol gRPC
![PyPI - Version](https://img.shields.io/pypi/v/aissemble-open-inference-protocol-grpc)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aissemble-open-inference-protocol-grpc)
![PyPI - Format](https://img.shields.io/pypi/format/aissemble-open-inference-protocol-grpc)
![PyPI - Downloads](https://img.shields.io/pypi/dm/aissemble-open-inference-protocol-grpc)
[![Build (github)](https://github.com/boozallen/aissemble-open-inference-protocol/actions/workflows/build.yaml/badge.svg)](https://github.com/boozallen/aissemble-open-inference-protocol/actions/workflows/build.yaml)

The [Open Inference Protocol (OIP)](https://github.com/kserve/open-inference-protocol) specification defines a standard protocol for performing machine learning model inference across serving runtimes for different ML frameworks. This Python application can be leveraged to create a gRPC server that is compatible with the Open Inference Protocol. It handles standing up and tearing down the server so you only need to worry about the inferencing functionality.

## Installation
Add `aissemble-open-inference-protocol-grpc` to an application
```bash
pip install aissemble-open-inference-protocol-grpc
```

## Usage

### Creating the Server
Use `aissemble-open-inference-protocol-grpc` to create a gRPC server by creating a file `main.py` with:
```python
import asyncio
from aissemble_open_inference_protocol_grpc.aissemble_oip_grpc import AissembleOIPgRPC

grpc = AissembleOIPgRPC()

if __name__ == '__main__':
    asyncio.run(grpc.start_server())
```
The gRPC server will come up after a few seconds and will be OIP compliant. The proto specifications can be found in the [grpc_inference_service.proto](https://github.com/boozallen/aissemble-open-inference-protocol/blob/dev/aissemble-open-inference-protocol-grpc/proto/grpc_inference_service.proto) file.

### Implementing the Endpoints Handler
By default, most of the gRPC endpoints will return a Method Not Implemented. You can implement these functions by creating a custom handler extending `DataplaneHandler`.

> [!NOTE]
> All incoming `InferenceRequest` and outgoing `InferenceResponse` objects will be automatically validated against their declared tensor shapes and datatypes. Any discrepancy will raise an error and abort the call.

Example:
```python
from typing import Optional

from aissemble_open_inference_protocol_shared.handlers.model_handler import (
    ModelHandler,
)
from aissemble_open_inference_protocol_shared.types.dataplane import (
    Datatype,
    InferenceRequest,
    InferenceResponse,
    ModelMetadataResponse,
    MetadataTensor,
)


class MyHandler(ModelHandler):
    def __init__(self):
        super().__init__()

    def infer(
            self,
            payload: InferenceRequest,
            model_name: str,
            model_version: Optional[str] = None,
    ) -> InferenceResponse:
        return InferenceResponse(
            model_name=model_name, model_version=model_version, id="id", outputs=[]
        )

    def model_metadata(
            self,
            model_name: str,
            model_version: Optional[str] = None,
    ) -> ModelMetadataResponse:
        return ModelMetadataResponse(
            name=model_name,
            versions=[model_version] if model_version else None,
            platform="python",
            inputs=[MetadataTensor(name="input", datatype=Datatype.FP32, shape=[1])],
            outputs=[
                MetadataTensor(name="output", datatype=Datatype.FP32, shape=[1])
            ],
        )

    def model_load(self, model_name: str) -> bool:
        # Do some model loading
        return True
```
Use `aissemble-open-inference-protocol-grpc` to create a gRPC server and pass it `MyHandler`
```python
from aissemble_open_inference_protocol_grpc.aissemble_oip_grpc import AissembleOIPgRPC

grpc = AissembleOIPgRPC(MyHandler())
```
Now when starting the server, the inference requests will route to the handler.

## Configuration
There are several configurations available that affect the server. These can be implemented via [Krausening](https://github.com/TechnologyBrewery/krausening/tree/dev/krausening-python/) properties file `oip.properties` or environment variables.

| Configuration Name         | Environment Variable       | Default Value             | Description                                                                                           |
|----------------------------|----------------------------|---------------------------|-------------------------------------------------------------------------------------------------------|
| `grpc_host`                | `GRPC_HOST`                | 0.0.0.0                   | The host the grpc server will start on                                                                |
| `grpc_port`                | `GRPC_PORT`                | 8081                      | The port the grpc server will start on                                                                |
| `grpc_workers`             | `GRPC_WORKERS`             | 3                         | Number of workers to be used by the server to execute non-AsyncIO RPC handlers                        |
| `auth_enabled`             | `AUTH_ENABLED`             | true                      | Whether authentication is enabled for the server. Strongly recommend enabling for higher environments |
| `auth_secret`              | `AUTH_SECRET`              | None                      | The secret key used to decode jwt token                                                               |
| `auth_algorithm`           | `AUTH_ALGORITHM`           | HS256                     | The algorithm used to decode jwt tokens                                                               |
| `pdp_url`                  | `OIP_PDP_URL`              | http://localhost:8080/pdp | The URL of the Policy Decision Point (PDP) used for authorization checks                              |


## Examples
For working examples, refer to the [Examples](https://github.com/boozallen/aissemble-open-inference-protocol/blob/dev/aissemble-open-inference-protocol-examples/README.md#grpc) documentation.
