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
from ...record.address import Address
from ...record.custom_data import CustomData
from pyspark.sql import Row
from .person_with_m_to_one_relation_field import PersonWithMToOneRelationField
from typing import Any, Dict
import jsonpickle

class PersonWithMToOneRelationBase(ABC):
    """
    Base implementation of the Record for PersonWithMToOneRelation.

    GENERATED CODE - DO NOT MODIFY (add your customizations in PersonWithMToOneRelation).

    Generated from: templates/data-delivery-data-records/record.base.py.vm
    """

    def __init__(self):
        """
        Default constructor for this record.
        """
        self._custom_field: str = None
        self._address: Address = None
        self._custom_data: CustomData = None


    @classmethod
    def from_row(cls, row: Row):
        """
        Creates a record with the given PySpark dataframe row's data.
        """
        record = cls()
        if row is not None:
            custom_field_value = cls.get_row_value(row, 'customField')
            record.custom_field = custom_field_value
            address_value = cls.get_row_value(row, 'Address')
            record.address = Address.from_row(address_value)
            custom_data_value = cls.get_row_value(row, 'CustomData')
            record.custom_data = CustomData.from_row(custom_data_value)
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
            self.address.as_row() if self.address is not None else None,
            self.custom_data.as_row() if self.custom_data is not None else None
        )


    @classmethod
    def from_dict(cls, dict_obj: Dict[str, Any]):
        """
        Creates a record with the given dictionary's data.
        """
        record = cls()
        if dict_obj is not None:
            record.custom_field = dict_obj.get('customField')
            if dict_obj.get('Address') is not None:
                record.address = Address.from_dict(dict_obj.get('Address'))
            if dict_obj.get('CustomData') is not None:
                record.custom_data = CustomData.from_dict(dict_obj.get('CustomData'))
            return record


    def as_dict(self) -> Dict[str, Any]:
        """
        Returns this record as a dictionary.
        """
        dict_obj = dict()

        dict_obj['customField'] = self.custom_field
        if self.address is not None:
            dict_obj['Address'] = self.address.as_dict()
        if self.custom_data is not None:
            dict_obj['CustomData'] = self.custom_data.as_dict()
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
    def address(self) -> Address:
        return self._address


    @address.setter
    def address(self, address:Address = None):
        self._address = address


    @property
    def custom_data(self) -> CustomData:
        return self._custom_data


    @custom_data.setter
    def custom_data(self, custom_data:CustomData = None):
        self._custom_data = custom_data


    def validate(self) -> None:
        """
        Performs the validation for this record.
        """
        self.validate_relations()


    def validate_relations(self) -> None:
        """
        Validate the reference records fields.
        """
        if self._address is None:
            raise ValueError('Relation record "Address" is required')
        else:
            self._address.validate()
        if self._custom_data is not None:
            self._custom_data.validate()

    def get_value_by_field(self, field: PersonWithMToOneRelationField) -> any:
        """
        Returns the value of the given field for this record.
        """
        value = None
        if field == PersonWithMToOneRelationField.CUSTOM_FIELD:
            value = self.custom_field

        return value
