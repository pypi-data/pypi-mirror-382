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
from ...dictionary.float_with_validation import FloatWithValidation
from ...dictionary.integer_with_validation import IntegerWithValidation
from .record_with_type_coercion_validation_field import RecordWithTypeCoercionValidationField
from typing import Any, Dict
import jsonpickle

class RecordWithTypeCoercionValidationBase(ABC):
    """
    Base implementation of the Record for RecordWithTypeCoercionValidation.

    GENERATED CODE - DO NOT MODIFY (add your customizations in RecordWithTypeCoercionValidation).

    Generated from: templates/data-delivery-data-records/record.base.py.vm
    """

    def __init__(self):
        """
        Default constructor for this record.
        """
        self._integer_validation: IntegerWithValidation = None
        self._float_validation: FloatWithValidation = None


    @classmethod
    def from_dict(cls, dict_obj: Dict[str, Any]):
        """
        Creates a record with the given dictionary's data.
        """
        record = cls()
        if dict_obj is not None:
            if dict_obj.get('integerValidation') is not None:
                record.integer_validation = IntegerWithValidation(dict_obj.get('integerValidation'))
            else:
                record.integer_validation = None
            if dict_obj.get('floatValidation') is not None:
                record.float_validation = FloatWithValidation(dict_obj.get('floatValidation'))
            else:
                record.float_validation = None
            return record


    def as_dict(self) -> Dict[str, Any]:
        """
        Returns this record as a dictionary.
        """
        dict_obj = dict()

        if self.integer_validation is not None:
            dict_obj['integerValidation'] = self.integer_validation.value
        else:
            dict_obj['integerValidation'] = None
        if self.float_validation is not None:
            dict_obj['floatValidation'] = self.float_validation.value
        else:
            dict_obj['floatValidation'] = None
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
    def integer_validation(self) -> IntegerWithValidation:
        return self._integer_validation


    @integer_validation.setter
    def integer_validation(self, integer_validation: IntegerWithValidation) -> None:
        self._integer_validation = integer_validation


    @property
    def float_validation(self) -> FloatWithValidation:
        return self._float_validation


    @float_validation.setter
    def float_validation(self, float_validation: FloatWithValidation) -> None:
        self._float_validation = float_validation


    def validate(self) -> None:
        """
        Performs the validation for this record.
        """
        self.validate_fields()


    def validate_fields(self) -> None:
        if self.integer_validation is not None:
            self.integer_validation.validate()

        if self.float_validation is not None:
            self.float_validation.validate()



    def get_value_by_field(self, field: RecordWithTypeCoercionValidationField) -> any:
        """
        Returns the value of the given field for this record.
        """
        value = None
        if field == RecordWithTypeCoercionValidationField.INTEGER_VALIDATION:
            value = self.integer_validation.value if self.integer_validation is not None else None
        if field == RecordWithTypeCoercionValidationField.FLOAT_VALIDATION:
            value = self.float_validation.value if self.float_validation is not None else None

        return value
