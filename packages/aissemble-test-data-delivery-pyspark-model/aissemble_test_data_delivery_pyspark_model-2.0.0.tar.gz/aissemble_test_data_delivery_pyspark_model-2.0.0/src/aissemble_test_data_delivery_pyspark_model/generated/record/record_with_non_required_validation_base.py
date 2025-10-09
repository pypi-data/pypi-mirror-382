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
from ...dictionary.integer_with_validation import IntegerWithValidation
from ...dictionary.string_with_validation import StringWithValidation
from pyspark.sql import Row
from .record_with_non_required_validation_field import RecordWithNonRequiredValidationField
from typing import Any, Dict
import jsonpickle

class RecordWithNonRequiredValidationBase(ABC):
    """
    Base implementation of the Record for RecordWithNonRequiredValidation.

    GENERATED CODE - DO NOT MODIFY (add your customizations in RecordWithNonRequiredValidation).

    Generated from: templates/data-delivery-data-records/record.base.py.vm
    """

    def __init__(self):
        """
        Default constructor for this record.
        """
        self._integer_validation: IntegerWithValidation = None
        self._string_validation: StringWithValidation = None
        self._string_simple: str = None


    @classmethod
    def from_row(cls, row: Row):
        """
        Creates a record with the given PySpark dataframe row's data.
        """
        record = cls()
        if row is not None:
            integer_validation_value = cls.get_row_value(row, 'integerValidation')
            record.integer_validation = IntegerWithValidation(integer_validation_value)
            string_validation_value = cls.get_row_value(row, 'stringValidation')
            record.string_validation = StringWithValidation(string_validation_value)
            string_simple_value = cls.get_row_value(row, 'stringSimple')
            record.string_simple = string_simple_value
        return record


    @classmethod
    def get_row_value(cls, row: Row, field: str) -> any:
        """
        Returns the value of a field in a PySpark dataframe row.
        """
        return row[field] if field in row else None


    def as_row(self) -> Row:
        """
        Returns this record as a PySpark dataframe row.
        """
        return Row(
            self.integer_validation.value if self.integer_validation is not None else None,
            self.string_validation.value if self.string_validation is not None else None,
            self.string_simple
        )


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
            if dict_obj.get('stringValidation') is not None:
                record.string_validation = StringWithValidation(dict_obj.get('stringValidation'))
            else:
                record.string_validation = None
            record.string_simple = dict_obj.get('stringSimple')
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
        if self.string_validation is not None:
            dict_obj['stringValidation'] = self.string_validation.value
        else:
            dict_obj['stringValidation'] = None
        dict_obj['stringSimple'] = self.string_simple
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
    def string_validation(self) -> StringWithValidation:
        return self._string_validation


    @string_validation.setter
    def string_validation(self, string_validation: StringWithValidation) -> None:
        self._string_validation = string_validation


    @property
    def string_simple(self) -> str:
        return self._string_simple


    @string_simple.setter
    def string_simple(self, string_simple: str) -> None:
        self._string_simple = string_simple


    def validate(self) -> None:
        """
        Performs the validation for this record.
        """
        self.validate_fields()


    def validate_fields(self) -> None:
        if self.integer_validation is not None:
            self.integer_validation.validate()

        if self.string_validation is not None:
            self.string_validation.validate()



    def get_value_by_field(self, field: RecordWithNonRequiredValidationField) -> any:
        """
        Returns the value of the given field for this record.
        """
        value = None
        if field == RecordWithNonRequiredValidationField.INTEGER_VALIDATION:
            value = self.integer_validation.value if self.integer_validation is not None else None
        if field == RecordWithNonRequiredValidationField.STRING_VALIDATION:
            value = self.string_validation.value if self.string_validation is not None else None
        if field == RecordWithNonRequiredValidationField.STRING_SIMPLE:
            value = self.string_simple

        return value
