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

import uvicorn
from fastapi import FastAPI, Request, HTTPException

from aissemble_open_inference_protocol_fastapi.rest import endpoints
from aissemble_open_inference_protocol_shared.aissemble_oip_service import (
    AissembleOIPService,
)
from aissemble_open_inference_protocol_shared.auth.auth_adapter_base import (
    AuthAdapterBase,
)
from aissemble_open_inference_protocol_shared.auth.default_adapter import (
    DefaultAdapter,
)
from aissemble_open_inference_protocol_shared.handlers.model_handler import (
    ModelHandler,
    DefaultModelHandler,
)


async def not_implemented_exception_handler(request: Request, exc: NotImplementedError):
    raise HTTPException(status_code=501, detail="Not Implemented")


class AissembleOIPFastAPI(AissembleOIPService):
    def __init__(
        self,
        model_handler: ModelHandler = DefaultModelHandler(),
        adapter: AuthAdapterBase = None,
    ):
        super().__init__(adapter, model_handler)
        self.server = FastAPI()
        self.server.include_router(endpoints.router)
        self.server.add_exception_handler(
            NotImplementedError, not_implemented_exception_handler
        )
        if self.model_handler is not None:
            self.server.dependency_overrides[DefaultModelHandler] = self._get_handler
        if self.adapter is not None:
            self.server.dependency_overrides[DefaultAdapter] = self._get_adapter

    def _get_handler(self):
        return self.model_handler

    def _get_adapter(self):
        return self.adapter

    async def start_server(self):
        config = uvicorn.Config(
            app=self.server,
            reload=self.config.fastapi_reload,
            host=self.config.fastapi_host,
            port=self.config.fastapi_port,
            use_colors=True,
        )
        server = uvicorn.Server(config=config)
        # Run FastAPI server
        await server.serve()
