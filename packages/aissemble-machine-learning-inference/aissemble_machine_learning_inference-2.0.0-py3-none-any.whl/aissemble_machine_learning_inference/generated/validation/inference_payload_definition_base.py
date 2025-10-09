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
# Disabling the no-self-argument as the validators are class methods. 

"""
    Base implementation of the request/response payloads for inference analytics.

    GENERATED CODE - DO NOT MODIFY (add your customizations in validation/inference_payload_definition.py).

    Generated from: templates/inference/inference.payload.base.py.vm
"""

from pydantic import BaseModel, validator
from ...dictionary.ip_address import IpAddress
from ...dictionary.event_kind import EventKind
from ...dictionary.event_category import EventCategory
from ...dictionary.event_outcome import EventOutcome
from ...dictionary.date_as_seconds_since_epoch import DateAsSecondsSinceEpoch

class RecordBase(BaseModel):
    """
    Represents a raw record in the inference request.
    """

    source_ip_address: str = None 

    @validator('source_ip_address')
    def validate_source_ip_address(cls, v):
        IpAddress(v).validate()
        return v

    created: int

    @validator('created')
    def validate_created(cls, v):
        DateAsSecondsSinceEpoch(v).validate()
        return v

    kind: str

    @validator('kind')
    def validate_kind(cls, v):
        EventKind(v).validate()
        return v

    category: str

    @validator('category')
    def validate_category(cls, v):
        EventCategory(v).validate()
        return v

    outcome: str

    @validator('outcome')
    def validate_outcome(cls, v):
        EventOutcome(v).validate()
        return v


class InferenceBase(BaseModel):
    """
    Represents an inference result of the model prediction.
    """

    score: int

    threat_detected: bool


