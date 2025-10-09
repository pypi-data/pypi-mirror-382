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
from ...dictionary.state_address import StateAddress
from ...dictionary.zipcode import Zipcode
from pyspark.sql import Row
from .address_field import AddressField
from typing import Any, Dict
import jsonpickle

class AddressBase(ABC):
    """
    Base implementation of the Record for Address.

    GENERATED CODE - DO NOT MODIFY (add your customizations in Address).

    Generated from: templates/data-delivery-data-records/record.base.py.vm
    """

    def __init__(self):
        """
        Default constructor for this record.
        """
        self._street: str = None
        self._city: str = None
        self._zipcode: Zipcode = None
        self._state: StateAddress = None


    @classmethod
    def from_row(cls, row: Row):
        """
        Creates a record with the given PySpark dataframe row's data.
        """
        record = cls()
        if row is not None:
            street_value = cls.get_row_value(row, 'street')
            record.street = street_value
            city_value = cls.get_row_value(row, 'city')
            record.city = city_value
            zipcode_value = cls.get_row_value(row, 'zipcode')
            record.zipcode = Zipcode(zipcode_value)
            state_value = cls.get_row_value(row, 'state')
            record.state = StateAddress(state_value)
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
            self.street,
            self.city,
            self.zipcode.value if self.zipcode is not None else None,
            self.state.value if self.state is not None else None
        )


    @classmethod
    def from_dict(cls, dict_obj: Dict[str, Any]):
        """
        Creates a record with the given dictionary's data.
        """
        record = cls()
        if dict_obj is not None:
            record.street = dict_obj.get('street')
            record.city = dict_obj.get('city')
            if dict_obj.get('zipcode') is not None:
                record.zipcode = Zipcode(dict_obj.get('zipcode'))
            else:
                record.zipcode = None
            if dict_obj.get('state') is not None:
                record.state = StateAddress(dict_obj.get('state'))
            else:
                record.state = None
            return record


    def as_dict(self) -> Dict[str, Any]:
        """
        Returns this record as a dictionary.
        """
        dict_obj = dict()

        dict_obj['street'] = self.street
        dict_obj['city'] = self.city
        if self.zipcode is not None:
            dict_obj['zipcode'] = self.zipcode.value
        else:
            dict_obj['zipcode'] = None
        if self.state is not None:
            dict_obj['state'] = self.state.value
        else:
            dict_obj['state'] = None
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
    def street(self) -> str:
        return self._street


    @street.setter
    def street(self, street: str) -> None:
        self._street = street


    @property
    def city(self) -> str:
        return self._city


    @city.setter
    def city(self, city: str) -> None:
        self._city = city


    @property
    def zipcode(self) -> Zipcode:
        return self._zipcode


    @zipcode.setter
    def zipcode(self, zipcode: Zipcode) -> None:
        self._zipcode = zipcode


    @property
    def state(self) -> StateAddress:
        return self._state


    @state.setter
    def state(self, state: StateAddress) -> None:
        self._state = state


    def validate(self) -> None:
        """
        Performs the validation for this record.
        """
        self.validate_fields()


    def validate_fields(self) -> None:
        if self.zipcode is not None:
            self.zipcode.validate()

        if self.state is not None:
            self.state.validate()



    def get_value_by_field(self, field: AddressField) -> any:
        """
        Returns the value of the given field for this record.
        """
        value = None
        if field == AddressField.STREET:
            value = self.street
        if field == AddressField.CITY:
            value = self.city
        if field == AddressField.ZIPCODE:
            value = self.zipcode.value if self.zipcode is not None else None
        if field == AddressField.STATE:
            value = self.state.value if self.state is not None else None

        return value
