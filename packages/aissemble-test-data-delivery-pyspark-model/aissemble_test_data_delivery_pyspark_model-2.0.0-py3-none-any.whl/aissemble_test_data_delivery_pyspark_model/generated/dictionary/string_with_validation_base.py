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
from re import fullmatch
from typing import List


class StringWithValidationBase(ABC):
    """
    Base implementation of the stringWithValidation dictionary type from PysparkDataDeliveryDictionary.

    GENERATED CODE - DO NOT MODIFY (add your customizations in StringWithValidation).

    Generated from: templates/data-delivery-data-records/dictionary.type.base.py.vm
    """

    MAX_LENGTH: int = int(50)
    MIN_LENGTH: int = int(5)
    FORMATS: List[str] = ['example-regex', '[A-Z]*[1-5]+', '\D*']


    def __init__(self, value: str):
        if value is not None:
            self._value = str(value)
        else:
            self._value = None


    @property
    def value(self) -> str:
        return self._value


    @value.setter
    def value(self, value: str) -> None:
        if value is not None:
            value = str(value)
            self._value = value
        else:
            self._value = None


    def validate(self) -> None:
        """
        Performs the validation for this dictionary type.
        """
        self.validate_length()
        self.validate_format()


    def validate_length(self) -> None:
        if self._value and self._value.strip() and len(self._value) > StringWithValidationBase.MAX_LENGTH:
            raise ValueError('StringWithValidation length of \'%s\' is greater than the maximum length of %s' % (self._value, StringWithValidationBase.MAX_LENGTH))
        if self._value and self._value.strip() and len(self._value) < StringWithValidationBase.MIN_LENGTH:
            raise ValueError('StringWithValidation length of \'%s\' is less than the minimum length of %s' % (self._value, StringWithValidationBase.MIN_LENGTH))


    def validate_format(self) -> None:
        if self._value and self._value.strip():
            validFormat = False
            for format in StringWithValidationBase.FORMATS:
                if fullmatch(format, self._value):
                    validFormat = True
                    break

            if not validFormat:
                raise ValueError('StringWithValidation value of \'%s\' did not match any valid formats' % self._value)
