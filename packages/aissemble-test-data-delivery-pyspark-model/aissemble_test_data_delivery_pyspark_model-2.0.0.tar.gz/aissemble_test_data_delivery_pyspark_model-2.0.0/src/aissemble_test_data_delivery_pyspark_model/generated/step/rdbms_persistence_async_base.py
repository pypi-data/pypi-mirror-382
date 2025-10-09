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
from aissemble_core_config import SparkRDBMSConfig
from pathlib import Path
from policy_manager.configuration import PolicyConfiguration
from typing import List
import os
from uuid import uuid4
from datetime import datetime

class RDBMSPersistenceAsyncBase(AbstractPipelineStep):
    """
    Performs scaffolding asynchronous processing for RDBMSPersistenceAsync. Business logic is delegated to the subclass.

    GENERATED CODE - DO NOT MODIFY (add your customizations in RDBMSPersistenceAsync).

    Generated from: templates/data-delivery-pyspark/asynchronous.processor.base.py.vm
    """

    logger = LogManager.get_instance().get_logger('RDBMSPersistenceAsyncBase')
    step_phase = 'RDBMSPersistenceAsync'
    bomIdentifier = "Unspecified RDBMSPersistenceAsync BOM identifier"



    def __init__(self, data_action_type, descriptive_label):
        super().__init__(data_action_type, descriptive_label)

        self.set_metadata_api_service(HiveMetadataAPIService())
        self.spark_rdbms_config = SparkRDBMSConfig()


    async def execute_step(self) -> None:
        """
        Executes this step.
        """
        start = time_ns()
        RDBMSPersistenceAsyncBase.logger.info('START: step execution...')

        run_id = uuid4()
        parent_run_facet = PipelineBase().get_pipeline_run_as_parent_run_facet()
        job_name = self.get_job_name()
        default_namespace = self.get_default_namespace()
        event_data = self.create_base_lineage_event_data()
        start_time = datetime.utcnow()
        self.record_lineage(self.create_lineage_start_event(run_id=run_id,job_name=job_name,default_namespace=default_namespace,parent_run_facet=parent_run_facet,event_data=event_data,start_time=start_time))
        try:
            await self.execute_step_impl()
            end_time = datetime.utcnow()
            self.record_lineage(self.create_lineage_complete_event(run_id=run_id,job_name=job_name,default_namespace=default_namespace,parent_run_facet=parent_run_facet,event_data=event_data,start_time=start_time,end_time=end_time))
        except Exception as error:
            self.logger.exception(
                "An exception occurred while executing "
                + self.descriptive_label
            )
            self.logger.exception(error)
            self.record_lineage(self.create_lineage_fail_event(run_id=run_id,job_name=job_name,default_namespace=default_namespace,parent_run_facet=parent_run_facet,event_data=event_data,start_time=start_time,end_time=datetime.utcnow(),error=error))
            PipelineBase().record_pipeline_lineage_fail_event()
            raise Exception(error)

        self.record_provenance()


        stop = time_ns()
        RDBMSPersistenceAsyncBase.logger.info('COMPLETE: step execution completed in %sms' % ((stop - start) / 1000000))
        


    @abstractmethod
    async def execute_step_impl(self) -> None:
        """
        This method performs the business logic of this step,
        and should be implemented in RDBMSPersistenceAsync.
        """
        pass


  

    def get_data_source_configs(self) -> dict:
        return {
            "url": self.spark_rdbms_config.jdbc_url(),
            "properties": {
                "user": self.spark_rdbms_config.user(),
                "password": self.spark_rdbms_config.password(),
                "driver": self.spark_rdbms_config.jdbc_driver()
            },
        }
    def save_dataset(self, dataset: DataFrame, table_name: str) -> None:
        RDBMSPersistenceAsyncBase.logger.info('Saving %s To RDBMS...' % self.descriptive_label)
        mode = "append"
        config = self.get_data_source_configs()
        dataset.write.jdbc(
            url=config.get("url"), table=table_name, mode=mode, properties=config.get("properties")
        )
        RDBMSPersistenceAsyncBase.logger.info('Saved %s to RDBMS' % self.descriptive_label)




    def get_logger(self):
        return self.logger
    
    def get_step_phase(self):
        return self.step_phase
