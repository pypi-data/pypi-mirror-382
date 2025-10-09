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
from pyspark.sql import Row
from .street_field import StreetField
from typing import Any, Dict
import jsonpickle

class StreetBase(ABC):
    """
    Base implementation of the Record for Street.

    GENERATED CODE - DO NOT MODIFY (add your customizations in Street).

    Generated from: templates/data-delivery-data-records/record.base.py.vm
    """

    def __init__(self):
        """
        Default constructor for this record.
        """
        self._name: str = None
        self._county: str = None
        self._integer_validation: IntegerWithValidation = None


    @classmethod
    def from_row(cls, row: Row):
        """
        Creates a record with the given PySpark dataframe row's data.
        """
        record = cls()
        if row is not None:
            name_value = cls.get_row_value(row, 'name')
            record.name = name_value
            county_value = cls.get_row_value(row, 'county')
            record.county = county_value
            integer_validation_value = cls.get_row_value(row, 'int_v8n')
            record.integer_validation = IntegerWithValidation(integer_validation_value)
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
            self.name,
            self.county,
            self.integer_validation.value if self.integer_validation is not None else None
        )


    @classmethod
    def from_dict(cls, dict_obj: Dict[str, Any]):
        """
        Creates a record with the given dictionary's data.
        """
        record = cls()
        if dict_obj is not None:
            record.name = dict_obj.get('name')
            record.county = dict_obj.get('county')
            if dict_obj.get('int_v8n') is not None:
                record.integer_validation = IntegerWithValidation(dict_obj.get('int_v8n'))
            else:
                record.integer_validation = None
            return record


    def as_dict(self) -> Dict[str, Any]:
        """
        Returns this record as a dictionary.
        """
        dict_obj = dict()

        dict_obj['name'] = self.name
        dict_obj['county'] = self.county
        if self.integer_validation is not None:
            dict_obj['int_v8n'] = self.integer_validation.value
        else:
            dict_obj['int_v8n'] = None
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
    def name(self) -> str:
        return self._name


    @name.setter
    def name(self, name: str) -> None:
        self._name = name


    @property
    def county(self) -> str:
        return self._county


    @county.setter
    def county(self, county: str) -> None:
        self._county = county


    @property
    def integer_validation(self) -> IntegerWithValidation:
        return self._integer_validation


    @integer_validation.setter
    def integer_validation(self, integer_validation: IntegerWithValidation) -> None:
        self._integer_validation = integer_validation


    def validate(self) -> None:
        """
        Performs the validation for this record.
        """
        self.validate_fields()


    def validate_fields(self) -> None:
        if self.integer_validation is not None:
            self.integer_validation.validate()



    def get_value_by_field(self, field: StreetField) -> any:
        """
        Returns the value of the given field for this record.
        """
        value = None
        if field == StreetField.NAME:
            value = self.name
        if field == StreetField.COUNTY:
            value = self.county
        if field == StreetField.INTEGER_VALIDATION:
            value = self.integer_validation.value if self.integer_validation is not None else None

        return value
