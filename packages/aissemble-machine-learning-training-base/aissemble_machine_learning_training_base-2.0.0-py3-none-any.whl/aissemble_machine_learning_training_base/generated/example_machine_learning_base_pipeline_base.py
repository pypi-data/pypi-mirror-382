###
# #%L
# aiSSEMBLE::Test::MDA::Machine Learning::Machine Learning Training Base
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

GENERATED CODE - DO NOT MODIFY (add your customizations in ExampleMachineLearningBasePipeline).

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


from .pipeline.pipeline_base import PipelineBase


class DatasetSplits(NamedTuple):
    """
    Class to store the training and test splits of a dataset.
    The splits are of type any, to allow for custom implementation
    for handling any number of datasets per split.
    """
    train: any
    test: any

class ExampleMachineLearningBasePipelineBase(ABC):
    """
    Base implementation of the pipeline.
    """
    logger = LogManager.get_instance().get_logger('ExampleMachineLearningBasePipeline')

    def __init__(self, experiment_name):
        """
        Default initializations for the pipeline.
        """
        # set default mlflow configurations
        self.config = PipelineConfig()
        mlflow.set_tracking_uri(self.config.mlflow_tracking_uri())
        mlflow.set_experiment(experiment_name)



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

        try:
            with mlflow.start_run() as run:
                self.training_run_id = run.info.run_id
                start = datetime.utcnow()
                loaded_dataset = self.load_dataset()
                prepped_dataset = self.prep_dataset(loaded_dataset)
                features = self.select_features(prepped_dataset)
                splits = self.split_dataset(prepped_dataset[features])
                model = self.train_model(splits.train)
                score = self.evaluate_model(model, splits.test)
                self.save_model(model)
                self.deploy_model(score, model)
                end = datetime.utcnow()
                self.log_information(start, end, loaded_dataset, features)
                self.logger.info('Complete')
        except Exception as error:
            raise Exception(error)


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
