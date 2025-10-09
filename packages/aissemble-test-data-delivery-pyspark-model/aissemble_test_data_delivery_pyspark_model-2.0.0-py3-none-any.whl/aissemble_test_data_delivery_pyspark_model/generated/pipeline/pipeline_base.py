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
from krausening.logging import LogManager
from openlineage.client.facet import ParentRunFacet
from uuid import uuid4, UUID
from aissemble_data_lineage import Emitter, LineageUtil

class PipelineBase:
    """
    Performs pipeline level process for PysparkDataDeliveryPatterns.

    GENERATED CODE - DO NOT MODIFY

    Generated from: templates/pipeline.base.py.vm
    """

    _instance = None
    _pipeline_run_id: UUID = None
    _pipeline_job_namespace: str = "PysparkDataDeliveryPatterns"
    _pipeline_name: str = "PysparkDataDeliveryPatterns"
    _pipeline_event_started = False
    _emitter: Emitter = None
    _lineage_util = LineageUtil()
    logger = LogManager.get_instance().get_logger('PipelineBase')


    def __new__(cls):
        """
        Create a singleton class for pipeline level process
        """
        if cls._instance is None:
            print("Creating the PipelineBase")
            cls._instance = super(PipelineBase, cls).__new__(cls)
        return cls._instance

    def record_pipeline_lineage_complete_event(self):
        """
        Record a pipeline lineage Complete event
        """
        if self._pipeline_event_started:
            if self._emitter is None:
                self._emitter = Emitter()

            self._lineage_util.record_lineage(self._emitter, self._lineage_util.create_complete_run_event(run_id=self.get_pipeline_run_id(), job_name=self._pipeline_name, default_namespace=self._pipeline_job_namespace))
            self._pipeline_event_started = False
            self._pipeline_run_id = None
            self.logger.info('Complete pipeline job run..')
        else:
            self.logger.warn("Pipeline hasn't recorded a lineage start event")

    def record_pipeline_lineage_fail_event(self):
        """
        Record a pipeline lineage Fail event
        """
        if self._pipeline_event_started:
            if self._emitter is None:
                self._emitter = Emitter()

            self._lineage_util.record_lineage(self._emitter, self._lineage_util.create_fail_run_event(run_id=self.get_pipeline_run_id(), job_name=self._pipeline_name, default_namespace=self._pipeline_job_namespace))
            self._pipeline_event_started = False
            self._pipeline_run_id = None
            self.logger.info('Fail pipeline job run..')
        else:
            self.logger.warn("Pipeline hasn't recorded a lineage start event")


    def record_pipeline_lineage_start_event(self):
        """
        Record a pipeline lineage Start event
        """
        if self._emitter is None:
            self._emitter = Emitter()

        # always make sure one job run at a time
        if not self._pipeline_event_started:
            run_event = self._lineage_util.create_start_run_event(run_id=self.get_pipeline_run_id(), job_name=self._pipeline_name, default_namespace=self._pipeline_job_namespace)
            self._pipeline_job_namespace = run_event.job.get_open_lineage_job().namespace
            self._lineage_util.record_lineage(self._emitter, run_event)
            self._pipeline_event_started = True
            self.logger.info('Start pipeline job run..')
        else:
            self.logger.warn("Pipeline has recorded a lineage start event");



    def get_pipeline_run_id(self) -> UUID:
        """
        Get the pipeline run id

        Returns:
            pipeline run id
        """
        if self._pipeline_run_id is None:
            self._pipeline_run_id = uuid4()
        return self._pipeline_run_id


    def get_pipeline_name(self) -> str:
        """
        Get the pipeline name

        Returns:
            pipeline name
        """
        return self._pipeline_name


    def get_pipeline_job_namespace(self) -> str:
        """
        Get the pipeline Job's namespace

        Returns:
            Namespace for the pipeline job
        """

        return self._pipeline_job_namespace


    def get_pipeline_run_as_parent_run_facet(self) -> ParentRunFacet:
        """
        Get the pipeline run event information as a ParentRunFacet

        Returns:
            ParentRunFacet created from pipeline run event information
        """

        if self._pipeline_run_id is not None:
            return ParentRunFacet(
                    run={"runId": str(self._pipeline_run_id)},
                    job={
                        "namespace": self._pipeline_job_namespace,
                        "name": self._pipeline_name,
                    },
                )





