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
from decimal import Decimal


class DecimalWithValidationBase(ABC):
    """
    Base implementation of the decimalWithValidation dictionary type from PysparkDataDeliveryDictionary.

    GENERATED CODE - DO NOT MODIFY (add your customizations in DecimalWithValidation).

    Generated from: templates/data-delivery-data-records/dictionary.type.base.py.vm
    """

    MAX_VALUE: Decimal = Decimal('100.0')
    MIN_VALUE: Decimal = Decimal('12.345')
    SCALE: int = int(3)


    def __init__(self, value: Decimal):
        if value is not None:
            self._value = Decimal(value)
        else:
            self._value = None


    @property
    def value(self) -> Decimal:
        return self._value


    @value.setter
    def value(self, value: Decimal) -> None:
        if value is not None:
            value = Decimal(value)
            self._value = round(value, DecimalWithValidationBase.SCALE)
        else:
            self._value = None


    def validate(self) -> None:
        """
        Performs the validation for this dictionary type.
        """
        self.validate_value()


    def validate_value(self) -> None:
        if (self._value is not None) and (self._value > DecimalWithValidationBase.MAX_VALUE):
            raise ValueError('DecimalWithValidation value of \'%s\' is greater than the maximum value of %s' % (self._value, DecimalWithValidationBase.MAX_VALUE))
        if (self._value is not None) and (self._value < DecimalWithValidationBase.MIN_VALUE):
            raise ValueError('DecimalWithValidation value of \'%s\' is less than the minimum value of %s' % (self._value, DecimalWithValidationBase.MIN_VALUE))
