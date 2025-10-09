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
from ...schema.citizen_schema import CitizenSchema
from ...schema.mayor_schema import MayorSchema
from ...schema.state_schema import StateSchema
from ...schema.street_schema import StreetSchema
from pyspark.sql.functions import bool_and, explode, monotonically_increasing_id, row_number
from pyspark.sql.types import ArrayType
from pyspark.sql.window import Window




class CitySchemaBase(ABC):
    """
    Base implementation of the PySpark schema for City.

    GENERATED CODE - DO NOT MODIFY (add your customizations in City).

    Generated from: templates/data-delivery-data-records/pyspark.schema.base.py.vm
    """

    MAYOR_COLUMN: str = 'MAYOR'
    STATE_COLUMN: str = 'STATE'
    STREET_COLUMN: str = 'STREET'
    CITIZEN_COLUMN: str = 'CITIZEN'


    def __init__(self):
        self._schema = StructType()
        self.validation_result_column = '__VALIDATE_RESULT_City_'

        self.add(self.MAYOR_COLUMN, MayorSchema().struct_type, True)
        self.add(self.STATE_COLUMN, StateSchema().struct_type, True)
        self.add(self.STREET_COLUMN, ArrayType(StreetSchema().struct_type), True)
        self.add(self.CITIZEN_COLUMN, ArrayType(CitizenSchema().struct_type), True)

    def cast(self, dataset: DataFrame) -> DataFrame:
        """
        Returns the given dataset cast to this schema.
        """
        mayor_type = self.get_data_type(self.MAYOR_COLUMN)
        state_type = self.get_data_type(self.STATE_COLUMN)
        street_type = self.get_data_type(self.STREET_COLUMN)
        citizen_type = self.get_data_type(self.CITIZEN_COLUMN)

        return dataset \
            .withColumn(self.MAYOR_COLUMN, dataset[self.MAYOR_COLUMN].cast(mayor_type)) \
            .withColumn(self.STATE_COLUMN, dataset[self.STATE_COLUMN].cast(state_type)) \
            .withColumn(self.STREET_COLUMN, dataset[self.STREET_COLUMN].cast(street_type)) \
            .withColumn(self.CITIZEN_COLUMN, dataset[self.CITIZEN_COLUMN].cast(citizen_type))


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
        # relation records validation
        # filter out null data for the required relation
        data_with_validations = data_with_validations.withColumn(self.validation_result_column + self.MAYOR_COLUMN + "_IS_NOT_NULL",
            col(column_prefix + self.MAYOR_COLUMN).isNotNull());

        mayor_schema = MayorSchema()
        data_with_validations = mayor_schema.validate_dataset_with_prefix(data_with_validations, 'MAYOR.', False)
        state_schema = StateSchema()
        data_with_validations = state_schema.validate_dataset_with_prefix(data_with_validations, 'STATE.', False)
        data_with_validations = self.with_street_validation(data_with_validations, 'STREET')
        # filter out null data for the required relation
        data_with_validations = data_with_validations.withColumn(self.validation_result_column + self.CITIZEN_COLUMN + "_IS_NOT_NULL",
            col(column_prefix + self.CITIZEN_COLUMN).isNotNull());

        data_with_validations = self.with_citizen_validation(data_with_validations, 'CITIZEN')

        # record fields validation

        column_filter_schemas = []
        validation_columns = [col for col in data_with_validations.columns if col not in ingest_dataset.columns]

        # Separate columns into groups based on their field name
        columns_grouped_by_field = []


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

    def with_street_validation(self, dataset: DataFrame, validation_column: str) -> DataFrame:
        """
        Validates the given Street 1:M multiplicity relation dataset against StreetSchema
        Returns A dataset with validation result __VALIDATE_STREET_COLUMN column
        """
        street_schema = StreetSchema()
        return self.validate_with_relation_record_schema(dataset, validation_column,
                    street_schema.validate_dataset_with_prefix, street_schema.validation_result_column,  False )

    def with_citizen_validation(self, dataset: DataFrame, validation_column: str) -> DataFrame:
        """
        Validates the given Citizen 1:M multiplicity relation dataset against CitizenSchema
        Returns A dataset with validation result __VALIDATE_CITIZEN_COLUMN column
        """
        citizen_schema = CitizenSchema()
        return self.validate_with_relation_record_schema(dataset, validation_column,
                    citizen_schema.validate_dataset_with_prefix, citizen_schema.validation_result_column,  True )


    def validate_with_relation_record_schema(self, ingest_dataset: DataFrame, validation_column: str, validate_dataset_with_prefix, relation_result_column: str, is_required=False) -> DataFrame:
        """
        Validates the given dataset with a given column where it contains array of ${relation.name} data records
        against ${relation.name} schema using the given validate_dataset_with_prefix and drop_validation_columns functions
        Returns the dataset including validation results in ${relation.name}_Valid column
        """
        id = "id"
        expanded_column = "expanded_column"
        aggregated_result_column = "bool_and({})".format(relation_result_column)
        result_column = "__VALIDATE_{}".format(validation_column)

        # add a row id
        ingest_dataset = ingest_dataset.withColumn(id, row_number().over(Window.orderBy(monotonically_increasing_id())))

        # flatten relation array record data for relation record validation
        validation_dataset = ingest_dataset.select(validation_column, id).withColumn(expanded_column, explode(validation_column)).drop(validation_column)

        # validate the flatten dataset
        validation_dataset = validate_dataset_with_prefix(validation_dataset, expanded_column + ".", False) \
            .drop(expanded_column)
        # group the validation result with original dataset row id
        validation_dataset = validation_dataset.groupBy(id).agg(bool_and(col(relation_result_column))) \
            .withColumn(result_column, col(aggregated_result_column))

        # cleanup
        validation_dataset = validation_dataset.drop(validation_column, aggregated_result_column)
        ingest_dataset = ingest_dataset.join(validation_dataset, id, "outer").drop(id)

        if is_required:
            ingest_dataset = ingest_dataset.withColumn(result_column, when(col(result_column).isNotNull() & col(result_column) == True, lit(True)).otherwise(lit(False)))
        else:
            ingest_dataset = ingest_dataset.withColumn(result_column, when(col(result_column).isNull() | col(result_column) == True, lit(True)).otherwise(lit(False)))

        return ingest_dataset

