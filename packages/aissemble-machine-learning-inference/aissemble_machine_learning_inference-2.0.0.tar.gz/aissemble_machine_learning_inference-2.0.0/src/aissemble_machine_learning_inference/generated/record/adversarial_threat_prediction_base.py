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
from abc import ABC
from .adversarial_threat_prediction_field import AdversarialThreatPredictionField
from typing import Any, Dict
import jsonpickle

class AdversarialThreatPredictionBase(ABC):
    """
    Base implementation of the Record for AdversarialThreatPrediction.

    GENERATED CODE - DO NOT MODIFY (add your customizations in AdversarialThreatPrediction).

    Generated from: templates/data-delivery-data-records/record.base.py.vm
    """

    def __init__(self):
        """
        Default constructor for this record.
        """
        self._score: int = None
        self._threat_detected: bool = None


    @classmethod
    def from_dict(cls, dict_obj: Dict[str, Any]):
        """
        Creates a record with the given dictionary's data.
        """
        record = cls()
        if dict_obj is not None:
            record.score = dict_obj.get('score')
            record.threat_detected = dict_obj.get('threatDetected')
            return record


    def as_dict(self) -> Dict[str, Any]:
        """
        Returns this record as a dictionary.
        """
        dict_obj = dict()

        dict_obj['score'] = self.score
        dict_obj['threatDetected'] = self.threat_detected
        return dict_obj


    @classmethod
    def from_json(cls, json_str: str):
        """
        Creates a record with the given json string's data.
        """
        dict_obj = jsonpickle.decode(json_str)
        return cls.from_dict(dict_obj)


    def as_json(self) -> str:
        """
        Returns this record as a json string.
        """
        return jsonpickle.encode(self.as_dict())


    @property
    def score(self) -> int:
        return self._score


    @score.setter
    def score(self, score: int) -> None:
        self._score = score


    @property
    def threat_detected(self) -> bool:
        return self._threat_detected


    @threat_detected.setter
    def threat_detected(self, threat_detected: bool) -> None:
        self._threat_detected = threat_detected


    def validate(self) -> None:
        """
        Performs the validation for this record.
        """
        self.validate_fields()


    def validate_fields(self) -> None:
        if self.score is None:
            raise ValueError('Field \'score\' is required')

        if self.threat_detected is None:
            raise ValueError('Field \'threatDetected\' is required')



    def get_value_by_field(self, field: AdversarialThreatPredictionField) -> any:
        """
        Returns the value of the given field for this record.
        """
        value = None
        if field == AdversarialThreatPredictionField.SCORE:
            value = self.score
        if field == AdversarialThreatPredictionField.THREAT_DETECTED:
            value = self.threat_detected

        return value
