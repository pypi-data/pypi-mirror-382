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
from pathlib import Path
from policy_manager.configuration import PolicyConfiguration
from typing import List
import os
from uuid import uuid4
from datetime import datetime

class PostgresPersistenceAsyncBase(AbstractPipelineStep):
    """
    Performs scaffolding asynchronous processing for PostgresPersistenceAsync. Business logic is delegated to the subclass.

    GENERATED CODE - DO NOT MODIFY (add your customizations in PostgresPersistenceAsync).

    Generated from: templates/data-delivery-pyspark/asynchronous.processor.base.py.vm
    """

    logger = LogManager.get_instance().get_logger('PostgresPersistenceAsyncBase')
    step_phase = 'PostgresPersistenceAsync'
    bomIdentifier = "Unspecified PostgresPersistenceAsync BOM identifier"



    def __init__(self, data_action_type, descriptive_label):
        super().__init__(data_action_type, descriptive_label)

        self.set_metadata_api_service(HiveMetadataAPIService())


    async def execute_step(self) -> None:
        """
        Executes this step.
        """
        start = time_ns()
        PostgresPersistenceAsyncBase.logger.info('START: step execution...')

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
        PostgresPersistenceAsyncBase.logger.info('COMPLETE: step execution completed in %sms' % ((stop - start) / 1000000))
        


    @abstractmethod
    async def execute_step_impl(self) -> None:
        """
        This method performs the business logic of this step,
        and should be implemented in PostgresPersistenceAsync.
        """
        pass


  

    def save_dataset(self, dataset: DataFrame, table_name: str) -> None:
        """
        Saves a dataset.
        """
        PostgresPersistenceAsyncBase.logger.warn('Persist type for test "postgres" is not yet supported by the aiSSEMBLE Solution Baseline!')
        PostgresPersistenceAsyncBase.logger.warn('Please encode persistence logic manually by overriding save_dataset(..)')




    def get_logger(self):
        return self.logger
    
    def get_step_phase(self):
        return self.step_phase
