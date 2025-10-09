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
from builtins import bytearray
from pyspark.sql import Row
from .custom_data_field import CustomDataField
from typing import Any, Dict
import jsonpickle

class CustomDataBase(ABC):
    """
    Base implementation of the Record for CustomData.

    GENERATED CODE - DO NOT MODIFY (add your customizations in CustomData).

    Generated from: templates/data-delivery-data-records/record.base.py.vm
    """

    def __init__(self):
        """
        Default constructor for this record.
        """
        self._custom_field: str = None
        self._binary_field: bytearray = None


    @classmethod
    def from_row(cls, row: Row):
        """
        Creates a record with the given PySpark dataframe row's data.
        """
        record = cls()
        if row is not None:
            custom_field_value = cls.get_row_value(row, 'customField')
            record.custom_field = custom_field_value
            binary_field_value = cls.get_row_value(row, 'binaryField')
            record.binary_field = binary_field_value
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
            self.custom_field,
            self.binary_field
        )


    @classmethod
    def from_dict(cls, dict_obj: Dict[str, Any]):
        """
        Creates a record with the given dictionary's data.
        """
        record = cls()
        if dict_obj is not None:
            record.custom_field = dict_obj.get('customField')
            record.binary_field = dict_obj.get('binaryField')
            return record


    def as_dict(self) -> Dict[str, Any]:
        """
        Returns this record as a dictionary.
        """
        dict_obj = dict()

        dict_obj['customField'] = self.custom_field
        dict_obj['binaryField'] = self.binary_field
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
    def custom_field(self) -> str:
        return self._custom_field


    @custom_field.setter
    def custom_field(self, custom_field: str) -> None:
        self._custom_field = custom_field


    @property
    def binary_field(self) -> bytearray:
        return self._binary_field


    @binary_field.setter
    def binary_field(self, binary_field: bytearray) -> None:
        self._binary_field = binary_field


    def validate(self) -> None:
        """
        Performs the validation for this record.
        """
        pass



    def get_value_by_field(self, field: CustomDataField) -> any:
        """
        Returns the value of the given field for this record.
        """
        value = None
        if field == CustomDataField.CUSTOM_FIELD:
            value = self.custom_field
        if field == CustomDataField.BINARY_FIELD:
            value = self.binary_field

        return value
