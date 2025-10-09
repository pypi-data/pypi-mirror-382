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

from pyspark.sql.dataframe import DataFrame
from pyspark.sql.column import Column
from pyspark.sql.types import StructType
from pyspark.sql.types import DataType
from pyspark.sql.functions import col, lit, when
from typing import List
import types
from pyspark.sql.types import IntegerType
from pyspark.sql.types import StringType




class StreetSchemaBase(ABC):
    """
    Base implementation of the PySpark schema for Street.

    GENERATED CODE - DO NOT MODIFY (add your customizations in Street).

    Generated from: templates/data-delivery-data-records/pyspark.schema.base.py.vm
    """

    NAME_COLUMN: str = 'name'
    COUNTY_COLUMN: str = 'county'
    INTEGER_VALIDATION_COLUMN: str = 'int_v8n'


    def __init__(self):
        self._schema = StructType()
        self.validation_result_column = '__VALIDATE_RESULT_Street_'

        self.add(self.NAME_COLUMN, StringType(), True)
        self.add(self.COUNTY_COLUMN, StringType(), True)
        self.add(self.INTEGER_VALIDATION_COLUMN, IntegerType(), True)

    def cast(self, dataset: DataFrame) -> DataFrame:
        """
        Returns the given dataset cast to this schema.
        """
        name_type = self.get_data_type(self.NAME_COLUMN)
        county_type = self.get_data_type(self.COUNTY_COLUMN)
        integer_validation_type = self.get_data_type(self.INTEGER_VALIDATION_COLUMN)

        return dataset \
            .withColumn(self.NAME_COLUMN, dataset[self.NAME_COLUMN].cast(name_type)) \
            .withColumn(self.COUNTY_COLUMN, dataset[self.COUNTY_COLUMN].cast(county_type)) \
            .withColumn(self.INTEGER_VALIDATION_COLUMN, dataset[self.INTEGER_VALIDATION_COLUMN].cast(integer_validation_type))


    @property
    def struct_type(self) -> StructType:
        """
        Returns the structure type for this schema.
        """
        return self._schema


    @struct_type.setter
    def struct_type(self, struct_type: StructType) -> None:
        raise Exception('Schema structure type should not be set manually!')


    def get_data_type(self, name: str) -> str:
        """
        Returns the data type for a field in this schema.
        """
        data_type = None
        if name in self._schema.fieldNames():
            data_type = self._schema[name].dataType

        return data_type


    def add(self, name: str, data_type: DataType, nullable: bool) -> None:
        """
        Adds a field to this schema.
        """
        self._schema.add(name, data_type, nullable)


    def update(self, name: str, data_type: DataType) -> None:
        """
        Updates the data type of a field in this schema.
        """
        fields = self._schema.fields
        if fields and len(fields) > 0:
            update = StructType()
            for field in fields:
                if field.name == name:
                    update.add(name, data_type, field.nullable)
                else:
                    update.add(field)

            self._schema = update

    def validate_dataset(self, ingest_dataset: DataFrame) -> DataFrame:
        return self.validate_dataset_with_prefix(ingest_dataset, "")

    def validate_dataset_with_prefix(self, ingest_dataset: DataFrame, column_prefix: str, valid_data_only = True) -> DataFrame:
        """
        Validates the given dataset and returns the lists of validated records.
        """
        data_with_validations = ingest_dataset

        # record fields validation
        data_with_validations = data_with_validations.withColumn(self.NAME_COLUMN + "_IS_NULL", col(column_prefix + self.NAME_COLUMN).isNull())
        data_with_validations = data_with_validations.withColumn(self.COUNTY_COLUMN + "_IS_NULL", col(column_prefix + self.COUNTY_COLUMN).isNull())
        data_with_validations = data_with_validations.withColumn(self.INTEGER_VALIDATION_COLUMN + "_IS_NULL", col(column_prefix + self.INTEGER_VALIDATION_COLUMN).isNull())
        data_with_validations = data_with_validations.withColumn(self.INTEGER_VALIDATION_COLUMN + "_GREATER_THAN_MIN", col(column_prefix + self.INTEGER_VALIDATION_COLUMN).cast('double') >= 100)
        data_with_validations = data_with_validations.withColumn(self.INTEGER_VALIDATION_COLUMN + "_LESS_THAN_MAX", col(column_prefix + self.INTEGER_VALIDATION_COLUMN).cast('double') <= 999)

        column_filter_schemas = []
        validation_columns = [col for col in data_with_validations.columns if col not in ingest_dataset.columns]

        # Separate columns into groups based on their field name
        columns_grouped_by_field = []

        columns_grouped_by_field.append([col for col in validation_columns if col.startswith(self.NAME_COLUMN)])
        columns_grouped_by_field.append([col for col in validation_columns if col.startswith(self.COUNTY_COLUMN)])
        columns_grouped_by_field.append([col for col in validation_columns if col.startswith(self.INTEGER_VALIDATION_COLUMN)])

        if valid_data_only:
            columns_grouped_by_field.append([col for col in validation_columns if col.startswith('__VALIDATE_')])

        # Create a schema filter for each field represented as a column group
        for column_group in columns_grouped_by_field:
            column_group_filter_schema = None

            # This column tracks if a non-required field is None. This enables
            # non-required validated fields to still pass filtering when they are None
            nullable_column = None

            for column_name in column_group:
                if column_name.endswith("_IS_NULL"):
                    nullable_column = col(column_name).eqNullSafe(True)
                elif column_group_filter_schema is not None:
                    column_group_filter_schema = column_group_filter_schema & col(column_name).eqNullSafe(True)
                else:
                    column_group_filter_schema = col(column_name).eqNullSafe(True)

            # Add the nullable column filter as a OR statement at the end of the given field schema
            # If there is no other schema filters for the field, then it can be ignored
            if nullable_column is not None and column_group_filter_schema is not None:
                column_group_filter_schema = nullable_column | column_group_filter_schema

            if column_group_filter_schema is not None:
                column_filter_schemas.append(column_group_filter_schema)

        # Isolate the valid data and drop validation columns
        valid_data = data_with_validations
        if column_filter_schemas:

            # Combine all the field filter schemas into one final schema for the row
            final_column_filter_schemas = None

            for column_group_filter_schema in column_filter_schemas:
                if  final_column_filter_schemas is not None:
                    final_column_filter_schemas = final_column_filter_schemas & column_group_filter_schema
                else:
                    final_column_filter_schemas = column_group_filter_schema

            if valid_data_only:
                valid_data = data_with_validations.filter(final_column_filter_schemas)
            else:
                valid_data = data_with_validations.withColumn(self.validation_result_column, when(final_column_filter_schemas, lit(True)).otherwise(lit(False)))
        else:
            if not valid_data_only:
                valid_data = data_with_validations.withColumn(self.validation_result_column, lit(True))

        valid_data = valid_data.drop(*validation_columns)
        return valid_data



