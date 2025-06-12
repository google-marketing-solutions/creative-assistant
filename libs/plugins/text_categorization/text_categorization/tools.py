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
"""Exposes text categorizer as a tool for Langchain agents."""

import os
from collections.abc import Sequence

import langchain_core
import pydantic

from text_categorization import categorizer, llms, vectorstore


class TextCategorizationInput(pydantic.BaseModel):
  """Input for text categorization."""

  texts: list[str] = pydantic.Field(description='texts to categorize')


class TextCategorizerTool(langchain_core.tools.BaseTool):
  """Tools that performs text categorization.

  Attributes:
    llm_type: Type of LLM to use for categorization.
    llm_parameters: Parameter for LLM initialization.
    examples_to_vectorstore: Whether to save example to vectorstore.
    name: Name of the tool.
    description: Description the tool.
    args_schema: Input model for the tool.
  """

  llm_type: str = 'gemini'
  llm_parameters: dict[str, str | float | None] = {
    'model': 'gemini-2.0-flash',
    'project': os.getenv('GOOGLE_CLOUD_PROJECT'),
    'temperature': 0.9,
  }
  examples_to_vectorstore: bool = False
  name: str = 'text_categorizer'
  description: str = 'categorizes texts into broader categories'
  args_schema: type[pydantic.BaseModel] = TextCategorizationInput

  def _run(
    self,
    texts: Sequence[str],
  ) -> list[dict[str, str]]:
    """Performs text categorization based on LLM and vectorstore.

    Args:
      texts: Texts that needs to be categorized.

    Returns:
      Mappings between text and its category.
    """
    llm = llms.create_categorizer_llm(self.llm_type, self.llm_parameters)
    text_categorizer = categorizer.TextCategorizer(
      llm=llm, vect_store=vectorstore.get_vector_store()
    )
    return text_categorizer.categorize(texts).to_list(row_type='dict')
