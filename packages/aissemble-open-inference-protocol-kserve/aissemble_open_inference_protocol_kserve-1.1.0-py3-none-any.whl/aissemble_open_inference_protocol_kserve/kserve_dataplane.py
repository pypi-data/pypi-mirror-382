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
from typing import Dict, Union, Optional, Tuple

from kserve import InferRequest, InferResponse, ModelRepository
from kserve.protocol.dataplane import DataPlane
from aissemble_open_inference_protocol_kserve.mappers.infer_mapper import InferMapper

from aissemble_open_inference_protocol_shared.handlers.dataplane import (
    DataplaneHandler,
)


class KServeDataplaneAdapter(DataPlane):
    """
    KServe DataPlane Adapter
    This class will convert aissemble-open-inference-protocol's DataplaneHandler to KServe's Dataplane Interface.
    """

    def __init__(self, handler: DataplaneHandler = DataplaneHandler()):
        super().__init__(model_registry=ModelRepository())
        self.handler = handler

    async def live(self) -> Dict[str, str]:
        """Server live
        Should return ``{"status": "alive"}`` on successful Server Live Check.
        """

        response = self.handler.server_live()
        if response.live:
            return {"status": "alive"}
        return {"status": "down"}

    async def ready(self) -> bool:
        """Server ready
        Should return True on successful Server Ready Check.
        """
        response = self.handler.server_ready()
        return response.live

    def metadata(self) -> Dict:
        """Server Metadata
        Returns a dictionary with following fields:
           - name (str): name of the server.
           - version (str): server version number.
           - extension (list[str]): list of extensions supported by this server
        """
        response = self.handler.server_metadata()
        return {
            "name": response.name,
            "version": response.version,
            "extensions": response.extensions,
        }

    async def model_metadata(self, model_name: str) -> Dict:
        """Model Metadata
        Returns a dictionary with following fields:
                - name (str): name of the model
                - platform: "" (Empty String)
                - inputs: Dict with below fields
                    - name (str): name of the input
                    - datatype (str): Eg. INT32, FP32
                    - shape ([]int): The shape of the tensor.
                                   Variable-size dimensions are specified as -1.
                - outputs: Same as inputs described above.
        NOTE: Model Version is not supported yet in KServe.
        """
        response = self.handler.model_metadata(model_name=model_name)

        model_input = []
        model_output = []
        for input in response.inputs:
            model_input.append(
                {"name": input.name, "datatype": input.datatype, "shape": input.shape}
            )
        for output in response.outputs:
            model_output.append(
                {
                    "name": output.name,
                    "datatype": output.datatype,
                    "shape": output.shape,
                }
            )

        return {
            "name": response.name,
            "platform": response.platform,
            "inputs": model_input,
            "outputs": model_output,
        }

    async def model_ready(
        self, model_name: str, disable_predictor_health_check: bool = False
    ) -> bool:
        """Model Ready
        Should return True on successful Model Ready Check.
        """
        response = self.handler.model_ready(model_name=model_name)
        return response.ready

    async def infer(
        self,
        model_name: str,
        request: Union[Dict, InferRequest],
        headers: Optional[Dict[str, str]] = None,
    ) -> Tuple[Union[Dict, InferResponse], Dict[str, str]]:
        """Inference endpoint
        Performs inference on the specified model with the provided body and headers:

         Args:
            model_name (str): Model name.
            request (Dict | InferRequest): Request body data.
            headers: (Optional[Dict[str, str]]): Request headers.

        Returns:
            Tuple[Union[Dict, InferResponse], Dict[str, str]]:
                - response: The inference result.
                - response_headers: Headers to construct the HTTP response.

        """
        inference_request = InferMapper.infer_request_to_inference_request(
            request=request
        )
        response = self.handler.infer(payload=inference_request, model_name=model_name)
        infer_response = InferMapper.inference_response_to_infer_response(
            response=response
        )

        response_headers = {}
        return infer_response, response_headers
