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
from ...generated.step.abstract_pipeline_step import AbstractPipelineStep
from krausening.logging import LogManager
from abc import abstractmethod
from time import time_ns
from ..pipeline.pipeline_base import PipelineBase
from pyspark.sql.dataframe import DataFrame
from aissemble_core_metadata.hive_metadata_api_service import HiveMetadataAPIService
from aissemble_core_config import SparkNeo4jConfig
from pathlib import Path
from policy_manager.configuration import PolicyConfiguration
import os
from typing import List
from uuid import uuid4
from datetime import datetime


class Neo4jPersistenceBase(AbstractPipelineStep):
    """
    Performs scaffolding synchronous processing for Neo4jPersistence. Business logic is delegated to the subclass.

    GENERATED CODE - DO NOT MODIFY (add your customizations in Neo4jPersistence).

    Generated from: templates/data-delivery-pyspark/synchronous.processor.base.py.vm
    """

    logger = LogManager.get_instance().get_logger('Neo4jPersistenceBase')
    step_phase = 'Neo4jPersistence'
    bomIdentifier = "Unspecified Neo4jPersistence BOM identifier"

    def __init__(self, data_action_type, descriptive_label):
        super().__init__(data_action_type, descriptive_label)

        self.set_metadata_api_service(HiveMetadataAPIService())
        self.spark_neo4j_config = SparkNeo4jConfig()


    def execute_step(self) -> None:
        """
        Executes this step.
        """
        start = time_ns()
        Neo4jPersistenceBase.logger.info('START: step execution...')

        run_id = uuid4()
        parent_run_facet = PipelineBase().get_pipeline_run_as_parent_run_facet()
        job_name = self.get_job_name()
        default_namespace = self.get_default_namespace()
        event_data = self.create_base_lineage_event_data()
        start_time = datetime.utcnow()
        self.record_lineage(self.create_lineage_start_event(run_id=run_id,job_name=job_name,default_namespace=default_namespace,parent_run_facet=parent_run_facet, event_data=event_data, start_time=start_time))
        try:
            self.execute_step_impl()
            end_time = datetime.utcnow()
            self.record_lineage(self.create_lineage_complete_event(run_id=run_id,job_name=job_name,default_namespace=default_namespace,parent_run_facet=parent_run_facet, event_data=event_data, start_time=start_time, end_time=end_time))
        except Exception as error:
            self.logger.exception(
                "An exception occurred while executing "
                + self.descriptive_label
            )
            self.record_lineage(self.create_lineage_fail_event(run_id=run_id,job_name=job_name,default_namespace=default_namespace,parent_run_facet=parent_run_facet, event_data=event_data, start_time=start_time, end_time=datetime.utcnow(), error=error))
            PipelineBase().record_pipeline_lineage_fail_event()
            raise Exception(error)

        self.record_provenance()


        stop = time_ns()
        Neo4jPersistenceBase.logger.info('COMPLETE: step execution completed in %sms' % ((stop - start) / 1000000))



    @abstractmethod
    def execute_step_impl(self) -> None:
        """
        This method performs the business logic of this step, 
        and should be implemented in Neo4jPersistence.
        """
        pass


  

    def save_dataset(self, dataset: DataFrame, labels: list) -> None:
        """
        Saves a dataset.
        """
        Neo4jPersistenceBase.logger.info('Saving %s To Neo4j...' % self.descriptive_label)

        options = self.spark_neo4j_config.get_spark_options()

        dataset.write \
            .format(SparkNeo4jConfig.NEO4J_FORMAT) \
            .options(**options) \
            .option(SparkNeo4jConfig.LABELS_OPTION, ':'.join(labels)) \
            .mode('append') \
            .save()

        Neo4jPersistenceBase.logger.info('Saved %s to Neo4j' % self.descriptive_label)




    def get_logger(self):
        return self.logger
    
    def get_step_phase(self):
        return self.step_phase
