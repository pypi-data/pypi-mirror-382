# Copyright 2021 IBM All Rights Reserved.
#
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

import unittest
from ibm_appconfiguration.configurations.internal.utils.metering import Metering


class MyTestCase(unittest.TestCase):

    def test_metering(self):

        metering = Metering.get_instance()
        metering.set_repeat_calls(False)
        # test features
        metering.add_metering(guid="guid1", environment_id="environment_id1", collection_id="collection_id1",
                              entity_id="id_1", segment_id="segment_id1", feature_id='feature_id1')
        metering.add_metering(guid="guid1", environment_id="environment_id1", collection_id="collection_id2",
                              entity_id="id_1", segment_id="segment_id1", feature_id='feature_id1')
        metering.add_metering(guid="guid1", environment_id="environment_id1", collection_id="collection_id2",
                              entity_id="id_1", segment_id="segment_id1", feature_id='feature_id1')

        metering.add_metering(guid="guid1", environment_id="environment_id2", collection_id="collection_id1",
                              entity_id="id_1", segment_id="segment_id1", property_id='property_id1')
        metering.add_metering(guid="guid1", environment_id="environment_id2", collection_id="collection_id2",
                              entity_id="id_1", segment_id="segment_id1", property_id='property_id1')
        metering.add_metering(guid="guid1", environment_id="environment_id2", collection_id="collection_id2",
                              entity_id="id_1", segment_id="$$null$$", property_id='property_id1')
        metering.add_metering(guid="guid1", environment_id="environment_id2", collection_id="collection_id2",
                              entity_id="id_6", segment_id="$$null$$", property_id='property_id1')
        metering.add_metering(guid="guid1", environment_id="environment_id2", collection_id="collection_id2",
                              entity_id="id_3", segment_id="$$null$$", property_id='property_id1')
        metering.add_metering(guid="guid1", environment_id="environment_id2", collection_id="collection_id2",
                              entity_id="id_4", segment_id="$$null$$", property_id='property_id1')
        metering.add_metering(guid="guid1", environment_id="environment_id2", collection_id="collection_id2",
                              entity_id="id_1", segment_id="$$null$$", property_id='property_id1')
        metering.add_metering(guid="guid1", environment_id="environment_id2", collection_id="collection_id2",
                              entity_id="id_1", segment_id="$$null$$", property_id='property_id1')
        metering.add_metering(guid="guid1", environment_id="environment_id2", collection_id="collection_id2",
                              entity_id="id_2", segment_id="$$null$$", property_id='property_id1')
        metering.add_metering(guid="guid1", environment_id="environment_id2", collection_id="collection_id2",
                              entity_id="id_5", segment_id="$$null$$", property_id='property_id1')

        result = metering.send_metering()
        print("result")

        # print(result)
        self.assertEqual(len(result["guid1"]), 4)


if __name__ == '__main__':
    unittest.main()
