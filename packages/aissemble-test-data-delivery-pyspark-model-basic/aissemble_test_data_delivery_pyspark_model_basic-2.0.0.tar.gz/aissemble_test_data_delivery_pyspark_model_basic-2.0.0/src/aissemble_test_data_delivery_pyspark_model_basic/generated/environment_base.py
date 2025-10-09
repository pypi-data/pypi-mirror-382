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
from data_delivery_spark_py.test_utils.spark_session_manager import create_standalone_spark_session

"""
Behave test environment setup to configure Spark for unit tests.

GENERATED CODE - DO NOT MODIFY (add your customizations in environment.py).

Originally generated from: templates/data-delivery-pyspark/behave.environment.base.py.vm
"""
logger = LogManager.get_instance().get_logger("Environment")


"""
Generated or model-dependent setup to be executed prior to unit tests.
"""
def initialize(sparkapplication_path = "target/apps/pyspark-data-delivery-basic-test-chart.yaml"):
    create_standalone_spark_session(sparkapplication_path)


"""
Generated or model-dependent setup to be executed after completion of unit tests.
"""
def cleanup():
    pass
