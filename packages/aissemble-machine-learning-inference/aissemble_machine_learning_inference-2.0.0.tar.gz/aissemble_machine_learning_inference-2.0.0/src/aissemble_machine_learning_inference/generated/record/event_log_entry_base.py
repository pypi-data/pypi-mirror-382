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
from ...dictionary.date_as_seconds_since_epoch import DateAsSecondsSinceEpoch
from ...dictionary.event_category import EventCategory
from ...dictionary.event_kind import EventKind
from ...dictionary.event_outcome import EventOutcome
from ...dictionary.ip_address import IpAddress
from .event_log_entry_field import EventLogEntryField
from typing import Any, Dict
import jsonpickle

class EventLogEntryBase(ABC):
    """
    Base implementation of the Record for EventLogEntry.

    GENERATED CODE - DO NOT MODIFY (add your customizations in EventLogEntry).

    Generated from: templates/data-delivery-data-records/record.base.py.vm
    """

    def __init__(self):
        """
        Default constructor for this record.
        """
        self._source_ip_address: IpAddress = None
        self._created: DateAsSecondsSinceEpoch = None
        self._kind: EventKind = None
        self._category: EventCategory = None
        self._outcome: EventOutcome = None


    @classmethod
    def from_dict(cls, dict_obj: Dict[str, Any]):
        """
        Creates a record with the given dictionary's data.
        """
        record = cls()
        if dict_obj is not None:
            if dict_obj.get('sourceIpAddress') is not None:
                record.source_ip_address = IpAddress(dict_obj.get('sourceIpAddress'))
            else:
                record.source_ip_address = None
            if dict_obj.get('created') is not None:
                record.created = DateAsSecondsSinceEpoch(dict_obj.get('created'))
            else:
                record.created = None
            if dict_obj.get('kind') is not None:
                record.kind = EventKind(dict_obj.get('kind'))
            else:
                record.kind = None
            if dict_obj.get('category') is not None:
                record.category = EventCategory(dict_obj.get('category'))
            else:
                record.category = None
            if dict_obj.get('outcome') is not None:
                record.outcome = EventOutcome(dict_obj.get('outcome'))
            else:
                record.outcome = None
            return record


    def as_dict(self) -> Dict[str, Any]:
        """
        Returns this record as a dictionary.
        """
        dict_obj = dict()

        if self.source_ip_address is not None:
            dict_obj['sourceIpAddress'] = self.source_ip_address.value
        else:
            dict_obj['sourceIpAddress'] = None
        if self.created is not None:
            dict_obj['created'] = self.created.value
        else:
            dict_obj['created'] = None
        if self.kind is not None:
            dict_obj['kind'] = self.kind.value
        else:
            dict_obj['kind'] = None
        if self.category is not None:
            dict_obj['category'] = self.category.value
        else:
            dict_obj['category'] = None
        if self.outcome is not None:
            dict_obj['outcome'] = self.outcome.value
        else:
            dict_obj['outcome'] = None
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
    def source_ip_address(self) -> IpAddress:
        return self._source_ip_address


    @source_ip_address.setter
    def source_ip_address(self, source_ip_address: IpAddress) -> None:
        self._source_ip_address = source_ip_address


    @property
    def created(self) -> DateAsSecondsSinceEpoch:
        return self._created


    @created.setter
    def created(self, created: DateAsSecondsSinceEpoch) -> None:
        self._created = created


    @property
    def kind(self) -> EventKind:
        return self._kind


    @kind.setter
    def kind(self, kind: EventKind) -> None:
        self._kind = kind


    @property
    def category(self) -> EventCategory:
        return self._category


    @category.setter
    def category(self, category: EventCategory) -> None:
        self._category = category


    @property
    def outcome(self) -> EventOutcome:
        return self._outcome


    @outcome.setter
    def outcome(self, outcome: EventOutcome) -> None:
        self._outcome = outcome


    def validate(self) -> None:
        """
        Performs the validation for this record.
        """
        self.validate_fields()


    def validate_fields(self) -> None:
        if self.source_ip_address is not None:
            self.source_ip_address.validate()

        if self.created is None:
            raise ValueError('Field \'created\' is required')
        else:
            self.created.validate()

        if self.kind is None:
            raise ValueError('Field \'kind\' is required')
        else:
            self.kind.validate()

        if self.category is None:
            raise ValueError('Field \'category\' is required')
        else:
            self.category.validate()

        if self.outcome is None:
            raise ValueError('Field \'outcome\' is required')
        else:
            self.outcome.validate()



    def get_value_by_field(self, field: EventLogEntryField) -> any:
        """
        Returns the value of the given field for this record.
        """
        value = None
        if field == EventLogEntryField.SOURCE_IP_ADDRESS:
            value = self.source_ip_address.value if self.source_ip_address is not None else None
        if field == EventLogEntryField.CREATED:
            value = self.created.value if self.created is not None else None
        if field == EventLogEntryField.KIND:
            value = self.kind.value if self.kind is not None else None
        if field == EventLogEntryField.CATEGORY:
            value = self.category.value if self.category is not None else None
        if field == EventLogEntryField.OUTCOME:
            value = self.outcome.value if self.outcome is not None else None

        return value
