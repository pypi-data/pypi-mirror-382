###
# #%L
# aiSSEMBLE::Open Inference Protocol::gRPC
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
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
from typing import Mapping


def merge_infer_parameters(protobuf_map: Mapping, value_dict: Mapping) -> Mapping:
    """
    Merge values from a dictionary into a protobuf map
    :param protobuf_map: the protobuf map to populate
    :param value_dict: dictionary of key-value pairs to merge into the map
    :return: the updated protobuf map
    """
    for key, value in value_dict.items():
        protobuf_map[key].MergeFrom(value)
    return protobuf_map


class MappingException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
