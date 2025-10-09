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
from abc import ABC, abstractmethod
from pyspark.sql import SparkSession
from krausening.properties import PropertyManager
from aissemble_core_metadata.metadata_model import MetadataModel
from aissemble_core_metadata.metadata_api import MetadataAPI
from aissemble_security.pdp_client import PDPClient
from aissembleauth.json_web_token_util import AissembleSecurityException
from aissembleauth.auth_config import AuthConfig
from uuid import uuid4, UUID
from aissemble_data_lineage import Run, Job, Emitter, RunEvent, from_open_lineage_facet, LineageUtil, LineageEventData
from openlineage.client.facet import ParentRunFacet
from aissemble_core_config import MessagingConfig
import os


class AbstractDataAction(ABC):
    """
    Contains the general concepts needed to perform a base aiSSEMBLE Reference Architecture Data Action.
    A Data Action is a step within a Data Flow.

    GENERATED CODE - DO NOT MODIFY (add your customizations in the step implementations).

    Generated from: templates/data-delivery-pyspark/abstract.data.action.py.vm
    """

    emitter: Emitter
    lineage_util: LineageUtil

    def __init__(self, data_action_type, descriptive_label):
        self.data_action_type = data_action_type
        self.descriptive_label = descriptive_label

        self.spark = self.create_spark_session('PysparkDataDeliveryPatterns')
        self.tailor_spark_logging_levels(self.spark)

        self.messaging_config = MessagingConfig()

        self.emitter = Emitter()
        self.lineage_util = LineageUtil()

    def create_spark_session(self, app_name: str) -> SparkSession:
        properties = PropertyManager.get_instance().get_properties(
            "spark-data-delivery.properties"
        )
        builder = SparkSession.builder
        if properties.getProperty("execution.mode.legacy", "false") == "true":
            builder = builder\
                .master("local[*]")\
                .config("spark.driver.host", "localhost")
        return builder.getOrCreate()

    def tailor_spark_logging_levels(self, spark: SparkSession) -> None:
        """
        Allows Spark logging levels to be tailored to prevent excessive logging.
        Override this method if needed.
        """
        logger = spark._jvm.org.apache.log4j
        logger.LogManager.getRootLogger().setLevel(logger.Level.WARN)
        logger.LogManager.getLogger('org.apache.spark.sql').setLevel(logger.Level.ERROR)

    def customize_run_event(self, event: RunEvent) -> RunEvent:
        """
        Override this method to modify the created RunEvent.  Provides an opportunity for adding customizations,
        such as Input or Output Datasets.

        The customize_run_event() function is now deprecated and should no longer be used for customizations.
        """
        return event

    def create_lineage_start_event(self, run_id: UUID = None, job_name: str = "", default_namespace: str = None, parent_run_facet: ParentRunFacet = None, event_data: LineageEventData = None, **kwargs) -> RunEvent:
        """
        Creates the Start RunEvent with given uuid, parent run facet, job name, lineage data event or any input parameters
        To customize the event, override the customize_lineage_start_event(...) function to include the job facets, run facets
        or the inputs/outputs dataset.

        The customize_run_event() is deprecated customize point.

        Returns:
            RunEvent created from the input arguments
        """
        event = self.lineage_util.create_start_run_event(
            run_id=run_id,
            parent_run_facet=parent_run_facet,
            job_name=job_name,
            default_namespace=default_namespace,
            event_data=event_data)
        event = self.customize_lineage_start_event(event, **kwargs)
        return self.customize_run_event(event)

    def create_lineage_complete_event(self, run_id: UUID = None, job_name: str = "", default_namespace: str = None, parent_run_facet: ParentRunFacet = None, event_data: LineageEventData = None, **kwargs) -> RunEvent:
        """
        Creates the Complete RunEvent with given uuid, parent run facet, job name, lineage data event or any input parameters
        To customize the event, override the customize_lineage_complete_event(...) function to include the job facets, run facets
        or the inputs/outputs dataset.

        The customize_run_event() is deprecated customize point.

        Returns:
            RunEvent created from the input arguments
        """
        event = self.lineage_util.create_complete_run_event(
            run_id=run_id,
            parent_run_facet=parent_run_facet,
            job_name=job_name,
            default_namespace=default_namespace,
            event_data=event_data)
        event = self.customize_lineage_complete_event(event, **kwargs)
        return self.customize_run_event(event)

    def create_lineage_fail_event(self, run_id: UUID = None, job_name: str = "", default_namespace: str = None, parent_run_facet: ParentRunFacet = None, event_data: LineageEventData = None, **kwargs) -> RunEvent:
        """
        Creates the Fail RunEvent with given uuid, parent run facet, job name, lineage data event or any input parameters
        To customize the event, override the customize_lineage_fail_event(...) function to include the job facets, run facets
        or the inputs/outputs dataset.

        The customize_run_event() is deprecated customize point.

        Returns:
            RunEvent created from the input arguments
        """
        event = self.lineage_util.create_fail_run_event(
            run_id=run_id,
            parent_run_facet=parent_run_facet,
            job_name=job_name,
            default_namespace=default_namespace,
            event_data=event_data)
        event = self.customize_lineage_fail_event(event, **kwargs)
        return self.customize_run_event(event)

    def record_lineage(self, event: RunEvent):
        """
        Records metadata for this step in an OpenLineage format.
        """
        self.lineage_util.record_lineage(self.emitter, event)

    def customize_lineage_start_event(self, event: RunEvent, **kwargs) -> RunEvent:
        """
        Customize the start event with the given input

        Returns
            lineage event
        """
        # Override this function to customize the lineage start event data
        return event

    def customize_lineage_complete_event(self, event: RunEvent, **kwargs) -> RunEvent:
        """
        Customize the complete event with the given input

        Returns
            lineage event
        """
        # Override this function to customize the lineage complete event data
        return event

    def customize_lineage_fail_event(self, event: RunEvent, **kwargs) -> RunEvent:
        """
        Customize the fail event with the given input

        Returns
            lineage event
        """
        # Override this function to customize the lineage fail event data
        return event

    def create_base_lineage_event_data(self) -> LineageEventData:
        """
        Create a base lineage event data that will included in all the step events

        Returns LineageEventData
        """
        return None

    def get_job_name(self) -> str:
        """
        The default Job name is the Step name. Override this function to change the default job name.
        """
        return "PysparkDataDeliveryPatterns.{}".format(self.get_step_phase())

    def get_default_namespace(self) -> str:
        """
        The default namespace is the Pipeline name. Override this function to change the default namespace.
        """
        return "PysparkDataDeliveryPatterns"
    def authorize(self, token: str, action: str):
        """
        Calls the Policy Decision Point server to authorize a jwt
        """
        auth_config = AuthConfig()

        if auth_config.is_authorization_enabled():
            pdp_client = PDPClient(auth_config.pdp_host_url())
            decision = pdp_client.authorize(token, "", action)

            if 'PERMIT' == decision:
                self.get_logger().info('User is authorized to run ' + self.get_step_phase())
            else:
                raise AissembleSecurityException('User is not authorized')


    def set_metadata_api_service(self, service: MetadataAPI):
        self.metadata_api_service = service

    def get_metadata_api_service(self) -> MetadataAPI:
        return self.metadata_api_service

    def get_provenance_resource_identifier(self) -> str:
        return "Unspecified " + self.get_step_phase() + " resource"

    @abstractmethod
    def get_logger(self):
        return
    
    @abstractmethod
    def get_step_phase(self):
        return

    def create_provenance_metadata(self) -> MetadataModel:
        """
        Controls creating the metadata that will be recorded for provenance purposes.
        """
        resource = self.get_provenance_resource_identifier()
        return MetadataModel(subject=self.data_action_type, action=self.descriptive_label, resource=resource)

    def record_provenance(self) -> None:
        """
        Records provenance for this step.
        """
        if self.get_metadata_api_service():
            self.get_logger().info('Recording provenance...')

            metadata = self.create_provenance_metadata()
            self.metadata_api_service.create_metadata(metadata)

            self.get_logger().info('Provenance recorded')
        else:
            self.get_logger().error('Provenance cannot be recorded without a valid Metadata API Service! '
                + 'Please make sure the service is set!')
