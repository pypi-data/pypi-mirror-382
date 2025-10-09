###
# #%L
# aiSSEMBLE::Open Inference Protocol::KServe
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
from kserve import Model, ModelServer

from aissemble_open_inference_protocol_kserve.kserve_dataplane import (
    KServeDataplaneAdapter,
)
from aissemble_open_inference_protocol_shared.aissemble_oip_service import (
    AissembleOIPService,
)
from aissemble_open_inference_protocol_shared.handlers.model_handler import ModelHandler


class AissembleOIPKServe(Model, AissembleOIPService):
    def __init__(
        self,
        name: str,
        model_handler: ModelHandler,
    ):
        Model.__init__(self, name)
        AissembleOIPService.__init__(self, adapter=None, model_handler=model_handler)

        # TODO now that we have abstracted the dataplane handler from the user, this model should be used instead of
        #  overriding Kserve's dph
        # Create a Kserve dataplane adapter to route requests to users model data.
        self.kserve_dataplane_adapter = KServeDataplaneAdapter(
            handler=self.dataplane_handler
        )
        self.model = None
        # initialize model ready false
        self.ready = False

    def load(self) -> bool:
        # update the model ready flag based on model_load() result
        self.ready = self.dataplane_handler.model_load(self.name)
        return self.ready

    def start_server(self):
        model_server = ModelServer(
            http_port=self.config.kserve_http_port,
            grpc_port=self.config.kserve_grpc_port,
            workers=self.config.kserve_workers,
            max_threads=self.config.kserve_max_threads,
            max_asyncio_workers=self.config.kserve_max_asyncio_workers,
            enable_grpc=self.config.kserve_enable_grpc,
            enable_docs_url=self.config.kserve_enable_docs_url,
            enable_latency_logging=self.config.kserve_enable_latency_logging,
            access_log_format=self.config.kserve_access_log_format,
        )
        model_server.dataplane = self.kserve_dataplane_adapter
        model_server.start([self])
