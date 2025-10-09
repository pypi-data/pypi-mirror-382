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


class IntegerWithValidationBase(ABC):
    """
    Base implementation of the integerWithValidation dictionary type from PysparkDataDeliveryDictionary.

    GENERATED CODE - DO NOT MODIFY (add your customizations in IntegerWithValidation).

    Generated from: templates/data-delivery-data-records/dictionary.type.base.py.vm
    """

    MAX_VALUE: int = int('999')
    MIN_VALUE: int = int('100')


    def __init__(self, value: int):
        if value is not None:
            self._value = int(value)
        else:
            self._value = None


    @property
    def value(self) -> int:
        return self._value


    @value.setter
    def value(self, value: int) -> None:
        if value is not None:
            value = int(value)
            self._value = value
        else:
            self._value = None


    def validate(self) -> None:
        """
        Performs the validation for this dictionary type.
        """
        self.validate_value()


    def validate_value(self) -> None:
        if (self._value is not None) and (self._value > IntegerWithValidationBase.MAX_VALUE):
            raise ValueError('IntegerWithValidation value of \'%s\' is greater than the maximum value of %s' % (self._value, IntegerWithValidationBase.MAX_VALUE))
        if (self._value is not None) and (self._value < IntegerWithValidationBase.MIN_VALUE):
            raise ValueError('IntegerWithValidation value of \'%s\' is less than the minimum value of %s' % (self._value, IntegerWithValidationBase.MIN_VALUE))
