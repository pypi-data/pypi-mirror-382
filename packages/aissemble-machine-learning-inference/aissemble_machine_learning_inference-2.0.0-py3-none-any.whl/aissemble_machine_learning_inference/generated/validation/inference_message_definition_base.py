###
# #%L
# aiSSEMBLE::Test::MDA::Machine Learning::Inference
# %%
# Copyright (C) 2021 Booz Allen
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
"""
    Base implementation of the message envelope for inference analytics.

    GENERATED CODE - DO NOT MODIFY (add your customizations in validation/inference_message_definition.py).

    Generated from: templates/inference/inference.message.base.py.vm
"""

from typing import Dict, List, Optional
from pydantic import BaseModel
from pandas import DataFrame

from ...validation.inference_payload_definition import Record, Inference

class RequestBodyBase(BaseModel):
    """
    Base class representing an inference request containing the data to use for the model prediction.
    """
    data: List[Record]

    def data_to_dict(self) -> Dict:
        """
        Convenience method to convert the data records into dictionaries.
        :return:
        """
        return [record.dict() for record in self.data]

    def prep_data(self) -> DataFrame:
        """
        Prep the data in the inference request for model prediction - override to
        provide the appropriate logic.
        :return:
        """

        return DataFrame(self.data_to_dict())


class ResponseBodyBase(BaseModel):
    """
    Base class representing a response containing the inference results of the model prediction.
    """
    inferences: List[Inference]
