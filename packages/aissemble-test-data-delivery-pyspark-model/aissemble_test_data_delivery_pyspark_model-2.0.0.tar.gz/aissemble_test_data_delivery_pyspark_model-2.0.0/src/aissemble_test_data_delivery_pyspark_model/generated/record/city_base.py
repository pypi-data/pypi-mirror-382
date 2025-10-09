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
from ...record.citizen import Citizen
from ...record.mayor import Mayor
from ...record.state import State
from ...record.street import Street
from pyspark.sql import Row
from typing import List
from .city_field import CityField
from typing import Any, Dict
import jsonpickle

class CityBase(ABC):
    """
    Base implementation of the Record for City.

    GENERATED CODE - DO NOT MODIFY (add your customizations in City).

    Generated from: templates/data-delivery-data-records/record.base.py.vm
    """

    def __init__(self):
        """
        Default constructor for this record.
        """
        self._mayor: Mayor = None
        self._state: State = None
        self._street: List[Street] = []
        self._citizen: List[Citizen] = []


    @classmethod
    def from_row(cls, row: Row):
        """
        Creates a record with the given PySpark dataframe row's data.
        """
        record = cls()
        if row is not None:
            mayor_value = cls.get_row_value(row, 'MAYOR')
            record.mayor = Mayor.from_row(mayor_value)
            state_value = cls.get_row_value(row, 'STATE')
            record.state = State.from_row(state_value)
            street_value = cls.get_row_value(row, 'STREET')
            record.street = [Street.from_row(street) for street in street_value]
            citizen_value = cls.get_row_value(row, 'CITIZEN')
            record.citizen = [Citizen.from_row(citizen) for citizen in citizen_value]
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
            self.mayor.as_row() if self.mayor is not None else None,
            self.state.as_row() if self.state is not None else None,
            [street.as_row() for street in self.street] if self.street is not None else None,
            [citizen.as_row() for citizen in self.citizen] if self.citizen is not None else None
        )


    @classmethod
    def from_dict(cls, dict_obj: Dict[str, Any]):
        """
        Creates a record with the given dictionary's data.
        """
        record = cls()
        if dict_obj is not None:
            if dict_obj.get('Mayor') is not None:
                record.mayor = Mayor.from_dict(dict_obj.get('Mayor'))
            if dict_obj.get('State') is not None:
                record.state = State.from_dict(dict_obj.get('State'))
            if dict_obj.get('Street') is not None:
                record.street = [Street.from_dict(street) for street in dict_obj.get('Street')]
            if dict_obj.get('Citizen') is not None:
                record.citizen = [Citizen.from_dict(citizen) for citizen in dict_obj.get('Citizen')]
            return record


    def as_dict(self) -> Dict[str, Any]:
        """
        Returns this record as a dictionary.
        """
        dict_obj = dict()

        if self.mayor is not None:
            dict_obj['Mayor'] = self.mayor.as_dict()
        if self.state is not None:
            dict_obj['State'] = self.state.as_dict()
        if self.street is not None and len(self.street) > 0:
            dict_obj['Street'] = [street.as_dict() for street in self.street]
        if self.citizen is not None and len(self.citizen) > 0:
            dict_obj['Citizen'] = [citizen.as_dict() for citizen in self.citizen]
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
    def mayor(self) -> Mayor:
        return self._mayor


    @mayor.setter
    def mayor(self, mayor:Mayor = None):
        self._mayor = mayor


    @property
    def state(self) -> State:
        return self._state


    @state.setter
    def state(self, state:State = None):
        self._state = state


    @property
    def street(self) -> List[Street]: 
        return self._street


    @street.setter
    def street(self, street:List[Street] = []): 
        self._street = street


    @property
    def citizen(self) -> List[Citizen]: 
        return self._citizen


    @citizen.setter
    def citizen(self, citizen:List[Citizen] = []): 
        self._citizen = citizen


    def validate(self) -> None:
        """
        Performs the validation for this record.
        """
        self.validate_relations()


    def validate_relations(self) -> None:
        """
        Validate the reference records fields.
        """
        if self._mayor is None:
            raise ValueError('Relation record "Mayor" is required')
        else:
            self._mayor.validate()
        if self._state is not None:
            self._state.validate()
        if self._street is not None:
            for street in self._street:
                street.validate()
        if self._citizen is None or len(self._citizen) == 0:
            raise ValueError('Relation record "Citizen" is required')
        else:
            for citizen in self._citizen:
                citizen.validate()

    def get_value_by_field(self, field: CityField) -> any:
        """
        Returns the value of the given field for this record.
        """
        value = None

        return value
