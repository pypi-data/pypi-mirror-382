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
import grpc
from grpc.aio import ServerInterceptor
from aissemble_open_inference_protocol_shared.config.oip_config import OIPConfig
import jwt

AUTH_ACTION_READ = "read"
AUTH_RESOURCE_DATA = "data"
AUTHORIZATION_HEADER = "authorization"
BEARER_PREFIX = "Bearer "


class AuthInterceptor(ServerInterceptor):
    """
    This interceptor verifies a Bearer JWT, decodes it using the configured secret and algorithm,
    then delegates to the provided auth_adapter to enforce resource-based access control.

    Args:
        auth_adapter: An adapter implementing .authorize(user, resource, action, user_ip, request_url, role).
    """

    def __init__(self, auth_adapter):
        self.auth_adapter = auth_adapter
        self.config = OIPConfig()

    def verify_jwt_token(self, token: str) -> dict:
        if not token.startswith(BEARER_PREFIX):
            raise jwt.InvalidTokenError("Invalid authorization header format")
        token = token[len(BEARER_PREFIX) :]
        secret_key = self.config.auth_secret()
        algorithm = self.config.auth_algorithm()
        return jwt.decode(token, secret_key, algorithms=[algorithm])

    async def intercept_service(self, continuation, handler_call_details):
        handler = await continuation(handler_call_details)
        # If auth is enabled but no protected endpoints are set, we will protect all endpoints.
        # Returning the handler here just passes through the request without any authorization checks.
        if handler is None:
            return handler

        # Wrap the unary_unary handler
        orig = handler.unary_unary
        if orig is None:
            return handler

        async def wrapped(request, context):
            """
            This wrapper is necessary because we need access to the context object at the point of request handling.
            It allows us to extract metadata like the user IP and authorization token, and to call context.abort if any stage of authorization fails.
            """
            # Pull IP from context
            peer = context.peer()  # e.g. "ipv4:1.2.3.4:56789"
            _, addr = peer.split(":", 1)
            ip, _ = addr.rsplit(":", 1)

            # Extract auth header
            metadata = dict(context.invocation_metadata())
            auth_header = metadata.get(AUTHORIZATION_HEADER, "")
            try:
                if not auth_header:
                    await context.abort(
                        grpc.StatusCode.UNAUTHENTICATED, "Missing token"
                    )
                    return
                token_data = self.verify_jwt_token(auth_header)

                allowed = self.auth_adapter.authorize(
                    user=token_data.get("sub"),
                    resource=AUTH_RESOURCE_DATA,
                    action=AUTH_ACTION_READ,
                    user_ip=ip,
                    request_url=handler_call_details.method,
                    role=token_data.get("roles", None),
                )
                if not allowed:
                    await context.abort(
                        grpc.StatusCode.UNAUTHENTICATED, "Not authorized"
                    )
                    return
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.PyJWTError):
                await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid token")
                return

            return orig(request, context)

        # Build new RpcMethodHandler with same serialization, but wrapped logic for accessing context
        return grpc.unary_unary_rpc_method_handler(
            wrapped,
            request_deserializer=handler.request_deserializer,
            response_serializer=handler.response_serializer,
        )
