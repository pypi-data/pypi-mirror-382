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
from abc import ABC, abstractmethod
from ...config.pipeline_config import PipelineConfig
from krausening.logging import LogManager


class CustomModelConversionBase(ABC):
    """
    Base custom model conversion post-action class.

    GENERATED CODE - DO NOT MODIFY (add your customizations in ExampleCustomConversion).

    Generated from: templates/post-action/model.conversion.base.py.vm
    """
    logger = LogManager.get_instance().get_logger('CustomModelConversionBase')


    def __init__(self) -> None:
        """
        Default constructor for a custom model conversion post-action.
        """
        self._pipeline_config = PipelineConfig()


    @property
    def converted_model_file_directory(self) -> str:
        """
        The directory to save the converted model to.

        :return: the directory so save the converted model to
        """
        return self._pipeline_config.onnx_model_directory()


    @property
    def converted_model_file_name(self) -> str:
        """
        The file name to save the converted model as.

        :return: the file name to save the converted model as
        """
        return 'converted_foo_model.onnx'


    @abstractmethod
    def _convert(self, source_model) -> any:
        """
        Performs the foo-to-custom conversion on the source model and returns the converted model.

        :source_model: the model to perform the conversion on
        :return: the converted model
        """
        pass


    @abstractmethod
    def _save(self, converted_model) -> None:
        """
        Saves the converted custom model.

        :converted_model: the converted model to save
        """
        pass


