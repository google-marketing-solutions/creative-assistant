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
"""Provides HTTP endpoint for text categorization."""

import fastapi

from text_categorization import categorizer, llms, vectorstore

app = fastapi.FastAPI()
llm = llms.create_categorizer_llm(
  llm_type='gemini', llm_parameters={'model': 'gemini-1.5-flash'}
)
text_categorizer = categorizer.TextCategorizer(
  llm=llm, vect_store=vectorstore.get_vector_store()
)


@app.post('/')
def categorize(
  data: dict[str, list[str]] = fastapi.Body(embed=True),
) -> list[dict[str, str]]:
  """Performs text categorization.

  Args:
    data: Contains texts for categorization.

  Returns:
    Category for each text.
  """
  return text_categorizer.categorize(data.get('texts')).to_list(row_type='dict')
