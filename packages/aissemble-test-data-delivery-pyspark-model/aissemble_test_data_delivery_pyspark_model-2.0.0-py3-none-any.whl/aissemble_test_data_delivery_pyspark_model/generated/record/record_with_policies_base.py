###
# #%L
# aiSSEMBLE::Test::MDA::Data Delivery Pyspark
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
from ...dictionary.type_with_policies import TypeWithPolicies
from .record_with_policies_field import RecordWithPoliciesField
from typing import Any, Dict
import jsonpickle

class RecordWithPoliciesBase(ABC):
    """
    Base implementation of the Record for RecordWithPolicies.

    GENERATED CODE - DO NOT MODIFY (add your customizations in RecordWithPolicies).

    Generated from: templates/data-delivery-data-records/record.base.py.vm
    """

    def __init__(self):
        """
        Default constructor for this record.
        """
        self._field_with_policies: str = None
        self._field_with_dictionary_type_policies: TypeWithPolicies = None
        self._field_with_dictionary_type_policies_overridden: TypeWithPolicies = None


    @classmethod
    def from_dict(cls, dict_obj: Dict[str, Any]):
        """
        Creates a record with the given dictionary's data.
        """
        record = cls()
        if dict_obj is not None:
            record.field_with_policies = dict_obj.get('fieldWithPolicies')
            if dict_obj.get('fieldWithDictionaryTypePolicies') is not None:
                record.field_with_dictionary_type_policies = TypeWithPolicies(dict_obj.get('fieldWithDictionaryTypePolicies'))
            else:
                record.field_with_dictionary_type_policies = None
            if dict_obj.get('fieldWithDictionaryTypePoliciesOverridden') is not None:
                record.field_with_dictionary_type_policies_overridden = TypeWithPolicies(dict_obj.get('fieldWithDictionaryTypePoliciesOverridden'))
            else:
                record.field_with_dictionary_type_policies_overridden = None
            return record


    def as_dict(self) -> Dict[str, Any]:
        """
        Returns this record as a dictionary.
        """
        dict_obj = dict()

        dict_obj['fieldWithPolicies'] = self.field_with_policies
        if self.field_with_dictionary_type_policies is not None:
            dict_obj['fieldWithDictionaryTypePolicies'] = self.field_with_dictionary_type_policies.value
        else:
            dict_obj['fieldWithDictionaryTypePolicies'] = None
        if self.field_with_dictionary_type_policies_overridden is not None:
            dict_obj['fieldWithDictionaryTypePoliciesOverridden'] = self.field_with_dictionary_type_policies_overridden.value
        else:
            dict_obj['fieldWithDictionaryTypePoliciesOverridden'] = None
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
    def field_with_policies(self) -> str:
        return self._field_with_policies


    @field_with_policies.setter
    def field_with_policies(self, field_with_policies: str) -> None:
        self._field_with_policies = field_with_policies


    @property
    def field_with_dictionary_type_policies(self) -> TypeWithPolicies:
        return self._field_with_dictionary_type_policies


    @field_with_dictionary_type_policies.setter
    def field_with_dictionary_type_policies(self, field_with_dictionary_type_policies: TypeWithPolicies) -> None:
        self._field_with_dictionary_type_policies = field_with_dictionary_type_policies


    @property
    def field_with_dictionary_type_policies_overridden(self) -> TypeWithPolicies:
        return self._field_with_dictionary_type_policies_overridden


    @field_with_dictionary_type_policies_overridden.setter
    def field_with_dictionary_type_policies_overridden(self, field_with_dictionary_type_policies_overridden: TypeWithPolicies) -> None:
        self._field_with_dictionary_type_policies_overridden = field_with_dictionary_type_policies_overridden


    def validate(self) -> None:
        """
        Performs the validation for this record.
        """
        pass



    def get_value_by_field(self, field: RecordWithPoliciesField) -> any:
        """
        Returns the value of the given field for this record.
        """
        value = None
        if field == RecordWithPoliciesField.FIELD_WITH_POLICIES:
            value = self.field_with_policies
        if field == RecordWithPoliciesField.FIELD_WITH_DICTIONARY_TYPE_POLICIES:
            value = self.field_with_dictionary_type_policies.value if self.field_with_dictionary_type_policies is not None else None
        if field == RecordWithPoliciesField.FIELD_WITH_DICTIONARY_TYPE_POLICIES_OVERRIDDEN:
            value = self.field_with_dictionary_type_policies_overridden.value if self.field_with_dictionary_type_policies_overridden is not None else None

        return value
