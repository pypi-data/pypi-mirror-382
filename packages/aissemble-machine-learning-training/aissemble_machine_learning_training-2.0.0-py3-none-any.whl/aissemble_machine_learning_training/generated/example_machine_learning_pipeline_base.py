###
# #%L
# aiSSEMBLE::Test::MDA::Machine Learning::Machine Learning Training
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
"""
Base implementation of this pipeline.

GENERATED CODE - DO NOT MODIFY (add your customizations in ExampleMachineLearningPipeline).

Generated from: templates/general-mlflow/training.base.py.vm
"""
from abc import ABC, abstractmethod
from typing import List, NamedTuple
from pandas import DataFrame
from ..config.pipeline_config import PipelineConfig
from datetime import datetime
import mlflow
import json
from aissemble_security.pdp_client import PDPClient
from aissembleauth.auth_config import AuthConfig
from pathlib import Path
from krausening.logging import LogManager

from ..post_action.example_onnx_sklearn_conversion import ExampleOnnxSklearnConversion
from ..post_action.example_onnx_keras_conversion import ExampleOnnxKerasConversion
from ..post_action.example_custom_conversion import ExampleCustomConversion
from ..post_action.example_freeform_post_action import ExampleFreeformPostAction

from .pipeline.pipeline_base import PipelineBase
from uuid import uuid4
from aissemble_data_lineage import Run, Job, Emitter, RunEvent, InputDataset, from_open_lineage_facet, LineageUtil, LineageEventData
from aissemble_model_lineage import MLflowRunFacet, LineageBuilder
from aissemble_core_config import MessagingConfig
import os
import attr

from openlineage.client.facet import ErrorMessageRunFacet, NominalTimeRunFacet, ParentRunFacet
from platform import python_version


class DatasetSplits(NamedTuple):
    """
    Class to store the training and test splits of a dataset.
    The splits are of type any, to allow for custom implementation
    for handling any number of datasets per split.
    """
    train: any
    test: any

class ExampleMachineLearningPipelineBase(ABC):
    """
    Base implementation of the pipeline.
    """
    logger = LogManager.get_instance().get_logger('ExampleMachineLearningPipeline')

    def __init__(self, experiment_name):
        """
        Default initializations for the pipeline.
        """
        # set default mlflow configurations
        self.config = PipelineConfig()
        mlflow.set_tracking_uri(self.config.mlflow_tracking_uri())
        mlflow.set_experiment(experiment_name)

        self.messaging_config = MessagingConfig()
        self.emitter = Emitter()
        self.lineage_builder = LineageBuilder()
        self.lineage_util = LineageUtil()


    @abstractmethod
    def acknowledge_training_alert(self, alert: any) -> None:
        """
        Method to acknowledge a training alert for auto-training purposes.
        """
        pass


    @abstractmethod
    def load_dataset(self) -> DataFrame:
        """
        Method to load a dataset for training.
        Returns a dataset of type DataFrame.
        """
        pass


    @abstractmethod
    def prep_dataset(self, dataset: DataFrame) -> DataFrame:
        """
        Method to perform last-mile data preparation on the loaded dataset.
        Returns the prepped dataset.
        """
        pass


    @abstractmethod
    def select_features(self, dataset: DataFrame) -> List[str]:
        """
        Method to perform feature selection on the prepped dataset.
        Returns a list of the features (columns) selected from the dataset.
        """
        pass


    @abstractmethod
    def split_dataset(self, dataset: DataFrame) -> DatasetSplits:
        """
        Method to create the train and test splits on the dataset with selected features.
        Returns the splits within a DatasetSplits object.
        """
        pass


    @abstractmethod
    def train_model(self, train_dataset: any) -> any:
        """
        Method to train a model with the training dataset split(s).
        Returns the model that has been trained.
        """
        pass


    @abstractmethod
    def evaluate_model(self, model: any, test_dataset: any) -> float:
        """
        Method to evaluate the trained model with the test dataset split(s).
        Returns the score of the model evaluation.
        """
        pass


    @abstractmethod
    def save_model(self, model: any) -> None:
        """
        Method to save the model to a location.
        """
        pass


    @abstractmethod
    def deploy_model(self, score: float, model: any) -> None:
        """
        Method to deploy the model if needed.
        """
        pass


    def run(self):
        """
        Runs the pipeline.
        """
        self.logger.info('Running %s...' % type(self).__name__)

        run_id = uuid4()
        parent_run_facet = PipelineBase().get_pipeline_run_as_parent_run_facet()
        job_name= self.get_job_name()
        try:
            with mlflow.start_run() as run:
                self.training_run_id = run.info.run_id
                event_data = self.create_base_lineage_event_data()
                default_namespace = self.get_default_namespace()
                start = datetime.utcnow()
                self.record_lineage(self.create_lineage_start_event(run_id=run_id, job_name=job_name, default_namespace=default_namespace, parent_run_facet=parent_run_facet, event_data=event_data, start_time=start))
                loaded_dataset = self.load_dataset()
                prepped_dataset = self.prep_dataset(loaded_dataset)
                features = self.select_features(prepped_dataset)
                splits = self.split_dataset(prepped_dataset[features])
                model = self.train_model(splits.train)
                score = self.evaluate_model(model, splits.test)
                self.save_model(model)
                self.deploy_model(score, model)
                self.apply_post_actions(self.training_run_id, model)
                end = datetime.utcnow()
                self.log_information(start, end, loaded_dataset, features)
                self.logger.info('Complete')
                self.record_lineage(self.create_lineage_complete_event(run_id=run_id, job_name=job_name, default_namespace=default_namespace, parent_run_facet=parent_run_facet, event_data=event_data, start_time=start, end_time=end))

        except Exception as error:
            self.record_lineage(self.create_lineage_fail_event(run_id=run_id, job_name=job_name, event_data=event_data, default_namespace=default_namespace, parent_run_facet=parent_run_facet, start_time=start, end_time=datetime.now(), error=error))
            PipelineBase().record_pipeline_lineage_fail_event()
            raise Exception(error)

    def apply_post_actions(self, training_run_id: str, model: any) -> None:
        """
        Applies the post actions specified for the training.
        """
        postActionExampleOnnxSklearnConversion = ExampleOnnxSklearnConversion(training_run_id, model)
        postActionExampleOnnxSklearnConversion.apply()

        postActionExampleOnnxKerasConversion = ExampleOnnxKerasConversion(training_run_id, model)
        postActionExampleOnnxKerasConversion.apply()

        postActionExampleCustomConversion = ExampleCustomConversion(training_run_id, model)
        postActionExampleCustomConversion.apply()

        postActionExampleFreeformPostAction = ExampleFreeformPostAction(training_run_id, model)
        postActionExampleFreeformPostAction.apply()

    def create_base_lineage_event_data(self) -> LineageEventData:
        """
        Create a base lineage event data that will included in all the step events

        Returns
            LineageEventData
        """
        job_facets = {
            "documentation": from_open_lineage_facet(self.lineage_builder.get_documentation_job_facet()),
            "ownership": from_open_lineage_facet(self.lineage_builder.get_ownership_job_facet()),
            "sourceCodeLocation": from_open_lineage_facet(self.lineage_builder.get_source_code_directory_job_facet())
        }
        run_facets = {
            "hardwareDetails": from_open_lineage_facet(self.lineage_builder.get_hardware_details_run_facet()),
            "hyperparameters": from_open_lineage_facet(self.lineage_builder.get_hyperparameter_run_facet()),
            "mlflowRunId": from_open_lineage_facet(MLflowRunFacet(self.training_run_id)),
            "performanceMetrics": from_open_lineage_facet(self.lineage_builder.get_performance_metric_run_facet())
        }
        dataset_facets = {
            "dataSource": from_open_lineage_facet(self.lineage_builder.get_data_source_dataset_facet()),
            "dataQualityAssertions": from_open_lineage_facet(self.lineage_builder.get_data_quality_assertions_facet()),
            "ownership": from_open_lineage_facet(self.lineage_builder.get_ownership_dataset_facet()),
            "schema": from_open_lineage_facet(self.lineage_builder.get_schema_dataset_facet()),
            "storage": from_open_lineage_facet(self.lineage_builder.get_storage_dataset_facet())
        }
        input_dataset = InputDataset("ExampleMachineLearningPipelineInput", dataset_facets)

        return LineageEventData(job_facets=job_facets, run_facets=run_facets, event_inputs=[input_dataset])

    def create_lineage_start_event(self, run_id: str = None, job_name: str = "", default_namespace:str = None, parent_run_facet: ParentRunFacet = None, event_data: LineageEventData = None, **kwargs) -> RunEvent:
        """
        Creates the Start RunEvent with given uuid, parent run facet, job name, lineage data event or any input parameters
        To customize the event, override the customize_lineage_start_event(...) function to include the job facets, run facets
        or the inputs/outputs dataset.

        The customize_run_event(..) is deprecated customize point.

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

    def customize_lineage_start_event(self, event: RunEvent = None, **kwargs) -> RunEvent:
        """
        Customize the start event with the given input

        Returns
            lineage event
        """

        if "start_time" in kwargs:
            run_facets = {
                "nominalTime": from_open_lineage_facet(NominalTimeRunFacet(kwargs["start_time"].isoformat(timespec="milliseconds") + "Z"))
            }
            event.run.facets.update(run_facets)

        return event

    def create_lineage_complete_event(self, run_id: str = None, job_name: str = "", default_namespace:str = None, parent_run_facet: ParentRunFacet = None, event_data: LineageEventData = None, **kwargs) -> RunEvent:
        """
        Creates the Complete RunEvent with given uuid, parent run facet, job name, lineage data event or any input parameters
        To customize the event, override the customize_lineage_complete_event(...) function to include the job facets, run facets
        or the inputs/outputs dataset.

        The customize_run_event(...) is deprecated customize point.

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

    def customize_lineage_complete_event(self, event: RunEvent = None, **kwargs) -> RunEvent:
        """
        Customize the complete event with the given input

        Returns
            lineage event
        """

        if "start_time" in kwargs and "end_time" in kwargs:
           event.run.facets.update(self.record_run_end(kwargs["start_time"], kwargs["end_time"]))
        return event

    def create_lineage_fail_event(self, run_id: str = None, job_name: str = "", default_namespace:str = None, parent_run_facet: ParentRunFacet = None, event_data: LineageEventData = None, **kwargs) -> RunEvent:
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

    def customize_lineage_fail_event(self, event: RunEvent = None, **kwargs) -> RunEvent:
        """
        Customize the fail event with the given input

        Returns
            lineage event
        """

        if "start_time" in kwargs and "end_time" in kwargs and "error" in kwargs:
           event.run.facets.update(self.record_run_end(kwargs["start_time"], kwargs["end_time"], kwargs["error"]))
        return event

    def customize_run_event(self, event: RunEvent) -> RunEvent:
        """
        Override this method to modify the created RunEvent.  Provides an opportunity for adding customizations,
        such as Input or Output Datasets.

        Returns:
            RunEvent with customizations added.
        """

        return event

    def record_run_end(self, start_time: datetime, end_time: datetime, error: Exception = None) -> None:
        """
        Records the end of the training run by updating the OpenLineage Run.  The end of the run can be due to successful
        completion of the logic or by an error.

        :param start_time: The start time of the training execution.
        :param end_time: The end time of the training execution.
        :param error: The `Exception` that caused the run to fail, if applicable. `None` if the run was successful.
        """

        run_end = { "nominalTime": from_open_lineage_facet(NominalTimeRunFacet(start_time.isoformat(timespec="milliseconds") + "Z", end_time.isoformat(timespec="milliseconds") + "Z"))}
        if error:
            run_end.update({"errorMessage": from_open_lineage_facet(ErrorMessageRunFacet(str(error), "Python"+python_version()))})

        return run_end

    def record_lineage(self, event: RunEvent):
        """
        Records metadata for this step in an OpenLineage format.
        """

        self.lineage_util.record_lineage(self.emitter, event)

    def get_job_name(self) -> str:
        """
        The default job name is the training step name; override this function to change the default job name
        """
        return "ExampleMachineLearningPipeline.AissembleMachineLearningTraining"

    def get_default_namespace(self) -> str:
        """
        The default namespace is the Pipeline name. Override this function to change the default namespace.
        """
        return "ExampleMachineLearningPipeline"

    def set_dataset_origin(self, origin: str) -> None:
        """
        Sets the origin of the dataset for a training run.
        """
        if not origin:
            self.logger.warning('No value given for dataset origin!')

        self.dataset_origin = origin


    def set_model_information(self, model_type: str, model_architecture: str) -> None:
        """
        Sets the model information for a training run.
        """
        if not model_type:
            self.logger.warning('No value given for model type!')
        if not model_architecture:
            self.logger.warning('No value given for model architecture!')

        self.model_type = model_type
        self.model_architecture = model_architecture


    def log_information(self, start: datetime, end: datetime, loaded_dataset: DataFrame, selected_features: List[str]) -> None:
        """
        Log information into MLflow tags.
        """
        try:
            mlflow.set_tags(
                {
                    "architecture": self.model_architecture,
                    "dataset_origin": self.dataset_origin,
                    "dataset_size": len(loaded_dataset),
                    "end_time": end,
                    "original_features": list(loaded_dataset),
                    "selected_features": selected_features,
                    "start_time": start,
                    "type": self.model_type,
                }
            )
        except Exception as error:
            raise Exception(error)


    def authorize(self, token: str, action: str):
        """
        Calls the Policy Decision Point server to authorize a jwt
        """

        auth_config = AuthConfig()

        pdp_client = PDPClient(auth_config.pdp_host_url())

        decision = pdp_client.authorize(token, "", action)

        return decision
