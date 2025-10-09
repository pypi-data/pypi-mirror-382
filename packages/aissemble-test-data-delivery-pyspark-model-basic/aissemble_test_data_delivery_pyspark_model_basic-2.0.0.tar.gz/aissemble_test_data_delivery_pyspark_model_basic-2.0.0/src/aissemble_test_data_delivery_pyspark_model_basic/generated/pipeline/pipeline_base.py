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
from krausening.logging import LogManager

class PipelineBase:
    """
    Performs pipeline level process for PysparkDataDeliveryBasic.

    GENERATED CODE - DO NOT MODIFY

    Generated from: templates/pipeline.base.py.vm
    """

    _instance = None
    logger = LogManager.get_instance().get_logger('PipelineBase')


    def __new__(cls):
        """
        Create a singleton class for pipeline level process
        """
        if cls._instance is None:
            print("Creating the PipelineBase")
            cls._instance = super(PipelineBase, cls).__new__(cls)
        return cls._instance






