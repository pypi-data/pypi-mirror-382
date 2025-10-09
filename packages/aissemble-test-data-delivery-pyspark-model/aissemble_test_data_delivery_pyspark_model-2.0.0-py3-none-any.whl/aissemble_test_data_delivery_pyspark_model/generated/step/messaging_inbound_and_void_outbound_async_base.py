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
from kafka import KafkaConsumer
import asyncio
import threading
from aissemble_core_config import MessagingConfig
from pathlib import Path
from policy_manager.configuration import PolicyConfiguration
from typing import List
import os
from pyspark.sql.functions import udf, col, lit, when
from pyspark.sql.types import StringType
from uuid import uuid4
from datetime import datetime

class MessagingInboundAndVoidOutboundAsyncBase(AbstractPipelineStep):
    """
    Performs scaffolding asynchronous processing for MessagingInboundAndVoidOutboundAsync. Business logic is delegated to the subclass.

    GENERATED CODE - DO NOT MODIFY (add your customizations in MessagingInboundAndVoidOutboundAsync).

    Generated from: templates/data-delivery-pyspark/asynchronous.processor.base.py.vm
    """

    logger = LogManager.get_instance().get_logger('MessagingInboundAndVoidOutboundAsyncBase')
    step_phase = 'MessagingInboundAndVoidOutboundAsync'
    bomIdentifier = "Unspecified MessagingInboundAndVoidOutboundAsync BOM identifier"

    consumer: KafkaConsumer | None


    def __init__(self, data_action_type, descriptive_label):
        super().__init__(data_action_type, descriptive_label)

        self.set_metadata_api_service(HiveMetadataAPIService())
        self.messaging_config = MessagingConfig()
        self.consumer = None


    def get_consumer_configs(self) -> dict:
        """
        Returns the configurations for the kafka consumer. Override this method to specify your own configurations.
        """
        return {
            'api_version': (2, 0, 2),
            'bootstrap_servers': [self.messaging_config.server()],
            'group_id': 'MessagingInboundAndVoidOutboundAsync',
            'auto_offset_reset': 'earliest'
        }


    async def execute_step(self) -> None:
        """
        Executes this step.
        """
        execute_step = threading.Thread(target=asyncio.run, args=(self.consume_from_kafka(),))
        execute_step.start()


    async def consume_from_kafka(self) -> None:
        self.consumer = KafkaConsumer("inboundChannel", **self.get_consumer_configs())

        for message in self.consumer:
            start = time_ns()
            MessagingInboundAndVoidOutboundAsyncBase.logger.info('START: step execution...')
            inbound = message.value.decode('utf-8')

            run_id = uuid4()
            job_name = self.get_job_name()
            default_namespace = self.get_default_namespace()
            parent_run_facet = PipelineBase().get_pipeline_run_as_parent_run_facet()
            event_data = self.create_base_lineage_event_data()
            start_time = datetime.utcnow()
            self.record_lineage(self.create_lineage_start_event(run_id=run_id,job_name=job_name,default_namespace=default_namespace,parent_run_facet=parent_run_facet,event_data=event_data,start_time=start_time))
            try:
                await self.execute_step_impl(inbound)
                end_time = datetime.utcnow()
                self.record_lineage(self.create_lineage_complete_event(run_id=run_id,job_name=job_name,default_namespace=default_namespace,parent_run_facet=parent_run_facet,event_data=event_data,start_time=start_time,end_time=end_time))
            except Exception as error:
                self.logger.exception(
                    "An exception occurred while executing "
                    + self.descriptive_label
                )
                self.record_lineage(self.create_lineage_fail_event(run_id=run_id,job_name=job_name,default_namespace=default_namespace,parent_run_facet=parent_run_facet,event_data=event_data,start_time=start_time,end_time=datetime.utcnow(),error=error))
                PipelineBase().record_pipeline_lineage_fail_event()
                raise Exception(error)

            self.record_provenance()


            self.consumer.commit()

            stop = time_ns()
            MessagingInboundAndVoidOutboundAsyncBase.logger.info('COMPLETE: step execution completed in %sms' % ((stop - start) / 1000000))

        self.consumer.close()


    @abstractmethod
    async def execute_step_impl(self, inbound: str) -> None:
        """
        This method performs the business logic of this step,
        and should be implemented in MessagingInboundAndVoidOutboundAsync.
        """
        pass





    def get_logger(self):
        return self.logger
    
    def get_step_phase(self):
        return self.step_phase
