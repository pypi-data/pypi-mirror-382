###
# #%L
# aiSSEMBLE::Test::MDA::Data Delivery Pyspark Basic
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
from pathlib import Path
from policy_manager.configuration import PolicyConfiguration
from typing import List
import os

class ExampleAsyncStepBase(AbstractPipelineStep):
    """
    Performs scaffolding asynchronous processing for ExampleAsyncStep. Business logic is delegated to the subclass.

    GENERATED CODE - DO NOT MODIFY (add your customizations in ExampleAsyncStep).

    Generated from: templates/data-delivery-pyspark/asynchronous.processor.base.py.vm
    """

    logger = LogManager.get_instance().get_logger('ExampleAsyncStepBase')
    step_phase = 'ExampleAsyncStep'
    bomIdentifier = "Unspecified ExampleAsyncStep BOM identifier"



    def __init__(self, data_action_type, descriptive_label):
        super().__init__(data_action_type, descriptive_label)



    async def execute_step(self) -> None:
        """
        Executes this step.
        """
        start = time_ns()
        ExampleAsyncStepBase.logger.info('START: step execution...')

        await self.execute_step_impl()



        stop = time_ns()
        ExampleAsyncStepBase.logger.info('COMPLETE: step execution completed in %sms' % ((stop - start) / 1000000))
        


    @abstractmethod
    async def execute_step_impl(self) -> None:
        """
        This method performs the business logic of this step,
        and should be implemented in ExampleAsyncStep.
        """
        pass



    def get_logger(self):
        return self.logger
    
    def get_step_phase(self):
        return self.step_phase
