# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import pytest
from garf_core import report as garf_report
from text_categorization import categorizer, llms


class TestCategorizer:
  @pytest.fixture
  def fake_llm(self):
    llm_responses = [
      """[{
        "text": "one",
        "category": "digit"
      }]""",
      """[{
        "text": "two",
        "category": "digit"
      }]""",
    ]

    return llms.create_categorizer_llm(
      llm_type='fake', llm_parameters={'responses': llm_responses}
    )

  def test_categorize_returns_correct_mapping(self, fake_llm):
    fake_categorizer = categorizer.TextCategorizer(llm=fake_llm)
    texts = ['one']
    result = fake_categorizer.categorize(texts)
    expected_result = garf_report.GarfReport(
      results=[
        ['one', 'digit'],
      ],
      column_names=['text', 'category'],
    )

    assert result == expected_result

  def test_categorize_returns_correct_mapping_with_subcategories(self):
    llm_responses = [
      """[{
        "text": "one",
        "category": "digit",
        "sub_category": "numeric"
      }]""",
      """[{
        "text": "two",
        "category": "digit",
        "sub_category": "numeric"
      }]""",
    ]

    fake_llm = llms.create_categorizer_llm(
      llm_type='fake', llm_parameters={'responses': llm_responses}
    )
    fake_categorizer = categorizer.TextCategorizer(
      llm=fake_llm, subcategory_needed=True
    )
    texts = ['one']
    result = fake_categorizer.categorize(texts)
    expected_result = garf_report.GarfReport(
      results=[
        ['one', 'digit', 'numeric'],
      ],
      column_names=['text', 'category', 'sub_category'],
    )

    assert result == expected_result
