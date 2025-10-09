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
from ...generated.post_action.custom_model_conversion_base import CustomModelConversionBase
from krausening.logging import LogManager


class ExampleCustomConversionBase(CustomModelConversionBase):
    """
    Base ExampleCustomConversion post-action class.

    GENERATED CODE - DO NOT MODIFY (add your customizations in ExampleCustomConversion).

    Generated from: templates/post-action/post.action.base.py.vm
    """
    logger = LogManager.get_instance().get_logger('ExampleCustomConversionBase')


    def __init__(self, training_run_id: str, model: any) -> None:
        """
        Default constructor for this post-action.

        :model: the model to apply this post-action on
        :training_run_id: the training run identifier associated with this post-action
        """
        super().__init__()
        self._training_run_id = training_run_id
        self._model = model


    @property
    def training_run_id(self) -> str:
        """
        The training run identifier associated with this post-action.

        :return: the training run identifier associated with this post-action.
        """
        return self._training_run_id


    @property
    def model(self) -> any:
        """
        The model to apply this post-action on.

        :return: the model to apply this post-action on
        """
        return self._model


    def apply(self) -> None:
        """
        Applies this model-conversion post-action.
        """
        ExampleCustomConversionBase.logger.info('Applying model conversion post action...')

        converted_model = self._convert(self.model)
        self._save(converted_model)

        ExampleCustomConversionBase.logger.info('Applied model conversion post action')
