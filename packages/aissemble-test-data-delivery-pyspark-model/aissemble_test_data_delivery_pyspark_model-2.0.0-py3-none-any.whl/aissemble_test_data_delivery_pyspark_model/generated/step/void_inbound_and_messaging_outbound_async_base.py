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
from aissemble_core_metadata.hive_metadata_api_service import HiveMetadataAPIService
from kafka import KafkaProducer
from aissemble_core_config import MessagingConfig
from pathlib import Path
from policy_manager.configuration import PolicyConfiguration
from typing import List
import os
from uuid import uuid4
from datetime import datetime

class VoidInboundAndMessagingOutboundAsyncBase(AbstractPipelineStep):
    """
    Performs scaffolding asynchronous processing for VoidInboundAndMessagingOutboundAsync. Business logic is delegated to the subclass.

    GENERATED CODE - DO NOT MODIFY (add your customizations in VoidInboundAndMessagingOutboundAsync).

    Generated from: templates/data-delivery-pyspark/asynchronous.processor.base.py.vm
    """

    logger = LogManager.get_instance().get_logger('VoidInboundAndMessagingOutboundAsyncBase')
    step_phase = 'VoidInboundAndMessagingOutboundAsync'
    bomIdentifier = "Unspecified VoidInboundAndMessagingOutboundAsync BOM identifier"


    producer: KafkaProducer | None

    def __init__(self, data_action_type, descriptive_label):
        super().__init__(data_action_type, descriptive_label)

        self.set_metadata_api_service(HiveMetadataAPIService())
        self.messaging_config = MessagingConfig()
        self.producer = KafkaProducer(**self.get_producer_configs())


    def get_producer_configs(self) -> dict:
        """
        Returns the configurations for the kafka producer. Override this method to specify your own configurations.
        """
        return {
            'api_version': (2, 0, 2),
            'bootstrap_servers': [self.messaging_config.server()],
        }


    async def execute_step(self) -> None:
        """
        Executes this step.
        """
        start = time_ns()
        VoidInboundAndMessagingOutboundAsyncBase.logger.info('START: step execution...')

        run_id = uuid4()
        parent_run_facet = PipelineBase().get_pipeline_run_as_parent_run_facet()
        job_name = self.get_job_name()
        default_namespace = self.get_default_namespace()
        event_data = self.create_base_lineage_event_data()
        start_time = datetime.utcnow()
        self.record_lineage(self.create_lineage_start_event(run_id=run_id,job_name=job_name,default_namespace=default_namespace,parent_run_facet=parent_run_facet,event_data=event_data,start_time=start_time))
        try:
            outbound = await self.execute_step_impl()
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

        if outbound is not None:
            self.producer.send('outboundChannel', value=outbound.encode())

        stop = time_ns()
        VoidInboundAndMessagingOutboundAsyncBase.logger.info('COMPLETE: step execution completed in %sms' % ((stop - start) / 1000000))
        


    @abstractmethod
    async def execute_step_impl(self) -> str:
        """
        This method performs the business logic of this step,
        and should be implemented in VoidInboundAndMessagingOutboundAsync.
        """
        pass





    def get_logger(self):
        return self.logger
    
    def get_step_phase(self):
        return self.step_phase
