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

from __future__ import absolute_import

import unittest
from ibm_appconfiguration.configurations.models import SegmentRules


class TestSegmentRules(unittest.TestCase):

    def test_empty_object(self):
        sut = SegmentRules(dict())
        self.assertEqual(sut.get_order(), 1)
        self.assertEqual(len(sut.get_rules()), 0)
        self.assertIsNotNone(sut.get_value())

    def test_object(self):
        segments = ["kg92d3wa"]
        json_seg_obj = {"segments": segments}
        rules = [json_seg_obj]
        segment_rules = {
            "rules": rules,
            "value": "IBM user",
            "order": 1
        }

        sut = SegmentRules(segment_rules)
        self.assertEqual(sut.get_order(), 1)
        self.assertEqual(len(sut.get_rules()), 1)
        self.assertEqual(sut.get_value(), "IBM user")


if __name__ == '__main__':
    unittest.main()
