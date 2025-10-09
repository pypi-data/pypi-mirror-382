###
# #%L
# aiSSEMBLE::Open Inference Protocol::FastAPI
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

from functools import partial
from typing import Optional

from fastapi import APIRouter, status, Depends, Request, HTTPException
from fastapi.security import HTTPBearer
from krausening.logging import LogManager

from aissemble_open_inference_protocol_shared.auth.auth_context import (
    AuthContext,
)
from aissemble_open_inference_protocol_shared.auth.default_adapter import (
    DefaultAdapter,
)
from aissemble_open_inference_protocol_shared.auth.jwt_auth import (
    authenticate_and_authorize,
)
from aissemble_open_inference_protocol_shared.codecs.utils import (
    decode_inference_request,
    build_inference_response,
)
from aissemble_open_inference_protocol_shared.handlers.dataplane import (
    DataplaneHandler,
)
from aissemble_open_inference_protocol_shared.handlers.model_handler import (
    DefaultModelHandler,
    ModelHandler,
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

security = HTTPBearer(auto_error=False)
AUTH_ACTION_READ = "read"
AUTH_RESOURCE_DATA = "data"

logger = LogManager.get_instance().get_logger("OIPEndpoints")

router = APIRouter(
    prefix="/v2",
    responses={404: {"description": "Not found"}},
)

# Partially initialize AuthContext with some common defaults
PartialAuthContext = partial(
    AuthContext,
    auth_action=AUTH_ACTION_READ,
    auth_resource=AUTH_RESOURCE_DATA,
)


@router.post(
    "/models/{model_name}/infer",
    summary="Perform a given models inference",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=InferenceResponse,
)
def infer_model(
    model_name,
    payload: InferenceRequest,
    request: Request,
    model_handler: DefaultModelHandler = Depends(DefaultModelHandler),
    authz_adapter: DefaultAdapter = Depends(DefaultAdapter),
    bearer_token: str = Depends(security),
) -> InferenceResponse:
    """
    Perform inference using the specified model and return the prediction results.
    """
    auth_context = PartialAuthContext(
        authz_adapter=authz_adapter,
        bearer_token=bearer_token,
        user_ip=_get_user_ip_from_request(request),
        request_url=str(request.url),
    )

    authenticate_and_authorize(auth_context)

    return infer(
        model_name=model_name,
        model_version=None,
        payload=payload,
        model_handler=model_handler,
    )


@router.post(
    "/models/{model_name}/versions/{model_version}/infer",
    summary="Perform a given models inference given a specific version",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=InferenceResponse,
)
async def infer_model_version(
    model_name,
    model_version,
    payload: InferenceRequest,
    request: Request,
    model_handler: DefaultModelHandler = Depends(DefaultModelHandler),
    authz_adapter: DefaultAdapter = Depends(DefaultAdapter),
    bearer_token: str = Depends(security),
) -> InferenceResponse:
    """
    Perform inference using the specified model version and return the prediction results.
    """
    auth_context = PartialAuthContext(
        authz_adapter=authz_adapter,
        bearer_token=bearer_token,
        user_ip=_get_user_ip_from_request(request),
        request_url=str(request.url),
    )
    authenticate_and_authorize(auth_context)

    return infer(
        model_name=model_name,
        model_version=model_version,
        payload=payload,
        model_handler=model_handler,
    )


def infer(
    model_name,
    model_version: Optional[str],
    payload: InferenceRequest,
    model_handler: ModelHandler,
) -> InferenceResponse:
    decoded_payload = decode_inference_request(payload)
    dataplane_handler = DataplaneHandler(model_handler)
    try:
        result = dataplane_handler.infer(
            model_name=model_name, model_version=model_version, payload=decoded_payload
        )
    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to validate InferenceResponse {e}",
        )
    return build_inference_response(
        model_name=model_name,
        request=payload,
        result=result,
        model_version=model_version,
    )


@router.get(
    "/models/{model_name}",
    summary="Get model metadata",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=ModelMetadataResponse,
)
def model_metadata(
    model_name: str,
    request: Request,
    model_handler: DefaultModelHandler = Depends(DefaultModelHandler),
    authz_adapter: DefaultAdapter = Depends(DefaultAdapter),
    bearer_token: str = Depends(security),
) -> ModelMetadataResponse:
    """
    Retrieve metadata for the specified model.
    """
    auth_context = PartialAuthContext(
        authz_adapter=authz_adapter,
        bearer_token=bearer_token,
        user_ip=_get_user_ip_from_request(request),
        request_url=str(request.url),
    )

    authenticate_and_authorize(auth_context)

    dataplane_handler = DataplaneHandler(model_handler)
    return dataplane_handler.model_metadata(model_name=model_name)


@router.get(
    "/models/{model_name}/versions/{model_version}",
    summary="Get model metadata for a specific version",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=ModelMetadataResponse,
)
def model_version_metadata(
    model_name: str,
    model_version: str,
    request: Request,
    model_handler: DefaultModelHandler = Depends(DefaultModelHandler),
    authz_adapter: DefaultAdapter = Depends(DefaultAdapter),
    bearer_token: str = Depends(security),
) -> ModelMetadataResponse:
    """
    Retrieve metadata for the specified model version.
    """
    auth_context = PartialAuthContext(
        authz_adapter=authz_adapter,
        bearer_token=bearer_token,
        user_ip=_get_user_ip_from_request(request),
        request_url=str(request.url),
    )

    authenticate_and_authorize(auth_context)

    dataplane_handler = DataplaneHandler(model_handler)
    return dataplane_handler.model_metadata(
        model_name=model_name, model_version=model_version
    )


@router.get(
    "/models/{model_name}/ready",
    summary="Check if model is ready",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=ModelReadyResponse,
)
def model_ready(
    model_name: str,
    request: Request,
    model_handler: DefaultModelHandler = Depends(DefaultModelHandler),
    authz_adapter: DefaultAdapter = Depends(DefaultAdapter),
    bearer_token: str = Depends(security),
) -> ModelReadyResponse:
    """
    Check if the specified model is ready to serve requests.
    """
    auth_context = PartialAuthContext(
        authz_adapter=authz_adapter,
        bearer_token=bearer_token,
        user_ip=_get_user_ip_from_request(request),
        request_url=str(request.url),
    )

    authenticate_and_authorize(auth_context)

    dataplane_handler = DataplaneHandler(model_handler)
    return dataplane_handler.model_ready(model_name=model_name)


@router.get(
    "/models/{model_name}/versions/{model_version}/ready",
    summary="Check if specific model version is ready",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=ModelReadyResponse,
)
def model_version_ready(
    model_name: str,
    model_version: str,
    request: Request,
    model_handler: DefaultModelHandler = Depends(DefaultModelHandler),
    authz_adapter: DefaultAdapter = Depends(DefaultAdapter),
    bearer_token: str = Depends(security),
) -> ModelReadyResponse:
    """
    Check if the specified model version is ready to serve requests.
    """
    auth_context = PartialAuthContext(
        authz_adapter=authz_adapter,
        bearer_token=bearer_token,
        user_ip=_get_user_ip_from_request(request),
        request_url=str(request.url),
    )

    authenticate_and_authorize(auth_context)

    dataplane_handler = DataplaneHandler(model_handler)
    return dataplane_handler.model_ready(
        model_name=model_name, model_version=model_version
    )


@router.get(
    "/health/ready",
    summary="Check if server is ready",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=ServerReadyResponse,
)
def server_ready(
    request: Request,
    model_handler: DefaultModelHandler = Depends(DefaultModelHandler),
    authz_adapter: DefaultAdapter = Depends(DefaultAdapter),
    bearer_token: str = Depends(security),
) -> ServerReadyResponse:
    """
    Check if the server returns the readiness probe.
    """
    auth_context = PartialAuthContext(
        authz_adapter=authz_adapter,
        bearer_token=bearer_token,
        user_ip=_get_user_ip_from_request(request),
        request_url=str(request.url),
    )

    authenticate_and_authorize(auth_context)

    dataplane_handler = DataplaneHandler(model_handler)
    return dataplane_handler.server_ready()


@router.get(
    "/health/live",
    summary="Check if server is live",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=ServerLiveResponse,
)
def server_live(
    request: Request,
    model_handler: DefaultModelHandler = Depends(DefaultModelHandler),
    authz_adapter: DefaultAdapter = Depends(DefaultAdapter),
    bearer_token: str = Depends(security),
) -> ServerLiveResponse:
    """
    Check if the server returns the liveness probe.
    """
    auth_context = PartialAuthContext(
        authz_adapter=authz_adapter,
        bearer_token=bearer_token,
        user_ip=_get_user_ip_from_request(request),
        request_url=str(request.url),
    )

    authenticate_and_authorize(auth_context)

    dataplane_handler = DataplaneHandler(model_handler)
    return dataplane_handler.server_live()


@router.get(
    "",
    summary="Get server metadata",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=ServerMetadataResponse,
)
def server_metadata(
    request: Request,
    model_handler: DefaultModelHandler = Depends(DefaultModelHandler),
    authz_adapter: DefaultAdapter = Depends(DefaultAdapter),
    bearer_token: str = Depends(security),
) -> ServerMetadataResponse:
    """
    Retrieve metadata for the server
    """
    auth_context = PartialAuthContext(
        authz_adapter=authz_adapter,
        bearer_token=bearer_token,
        user_ip=_get_user_ip_from_request(request),
        request_url=str(request.url),
    )

    authenticate_and_authorize(auth_context)

    dataplane_handler = DataplaneHandler(model_handler)
    return dataplane_handler.server_metadata()


def _get_user_ip_from_request(request: Request):
    """
    Extracts the user's IP address from the request object, respecting the
    `x-forwarded-for` header if present.
    :param request:  The FastAPI request object
    :return: The IP address of the user
    """
    forwarded = request.headers.get("x-forwarded-for")

    ip = request.client.host

    if forwarded:
        try:
            ip = forwarded.split(",")[0].strip()
        except Exception as e:
            logger.warning(
                f"Request header has x-forwarded-for ({forwarded}), but unable to extract ip.",
                e,
            )

    return ip
