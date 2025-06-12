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
"""Performs text categorization based on one or several categorizers."""

import functools
import itertools
import operator
import pathlib
from collections.abc import Mapping, Sequence
from concurrent import futures
from typing import Final, Generator

import pydantic
import smart_open
from garf_core import report as garf_report
from langchain_core import exceptions as langchain_exceptions
from langchain_core import (
  language_models,
  output_parsers,
  prompts,
  runnables,
  vectorstores,
)

from text_categorization import vectorstore

_BATCH_SIZE: Final[int] = 100


class Category(pydantic.BaseModel):
  """Helper class for formatting output of categorize method."""

  text: str = pydantic.Field(description='text')
  category: str = pydantic.Field(description='text_category')


class CategoryWithSubCategory(pydantic.BaseModel):
  """Helper class for formatting output of categorize method."""

  text: str = pydantic.Field(description='text')
  category: str = pydantic.Field(description='text_category')
  sub_category: str = pydantic.Field(description='text_sub_category')


class TextCategorizer:
  """Handles text categorization through LLMs.

  Attributes:
    llm: Initialized language model.
    vect_store: Vector store with text categories.
  """

  def __init__(
    self,
    llm: language_models.BaseLanguageModel,
    vect_store: vectorstores.VectorStore | None = None,
    subcategory_needed: bool = False,
  ) -> None:
    """Initializes TextCategorizer.

    Args:
      llm: Initialized language model.
      vect_store: Vector store with text categories.
      subcategory_needed: Whether category should contain a subcategory.
    """
    self.vect_store = vect_store
    self.llm = llm
    self.examples = ''
    if subcategory_needed:
      self._output_object = CategoryWithSubCategory
    else:
      self._output_object = Category

  def add_examples(
    self, examples: Sequence[str], load_to_vectorstore: bool = False
  ) -> None:
    """Provides examples for LLM categorization."""
    self.examples = examples
    if load_to_vectorstore and self.vect_store:
      self.vect_store.add_texts(examples)

  @property
  def prompt(self) -> prompts.PromptTemplate:
    """Builds correct prompt to send to LLM.

    Prompt contains format instructions to get output result.
    """
    with smart_open.open(
      pathlib.Path(__file__).resolve().parent / 'template.txt',
      'r',
      encoding='utf-8',
    ) as f:
      template = f.readlines()
    return prompts.PromptTemplate(
      template=' '.join(template),
      input_variables=['query'],
      partial_variables={
        'format_instructions': self.output_parser.get_format_instructions(),
        'examples': self.examples,
      },
    )

  @property
  def output_parser(self) -> output_parsers.BaseOutputParser:
    """Defines how LLM response should be formatted."""
    return output_parsers.JsonOutputParser(pydantic_object=self._output_object)

  @property
  def chain(self):
    """Lanchain chain with injected examples."""
    if self.vect_store:
      return (
        {
          'examples': self.vect_store.as_retriever() | vectorstore.format_docs,
          'question': runnables.RunnablePassthrough(),
        }
        | self.prompt
        | self.llm
        | self.output_parser
      )
    return self.prompt | self.llm | self.output_parser

  def categorize(
    self,
    texts: Sequence[str],
    max_parallel_workers: int = 10,
    batch_size: int = _BATCH_SIZE,
  ) -> garf_report.GarfReport:
    """Performs text categorization.

    Args:
      texts: Texts that needs to be categorized.
      max_parallel_workers: How many parallel threads to launch.
      batch_size: How many texts should be taken in for categorization.

    Returns:
      Report with mapping of text to a category.
    """
    if len(texts) <= batch_size:
      results = []
      column_names = list(
        self.output_parser.pydantic_object.__annotations__.keys()
      )
      try:
        result = self.chain.invoke(texts)
      except langchain_exceptions.OutputParserException:
        result = [self._safe_invoke_chain(text) for text in texts]
      if not result:
        return garf_report.GarfReport(
          results=results, column_names=column_names
        )
      for r in result:
        try:
          results.append([*r.values()])
        except AttributeError:
          results.append([r])
      return garf_report.GarfReport(results=results, column_names=column_names)
    reports: list[garf_report.GarfReport] = []
    with futures.ThreadPoolExecutor(
      max_workers=max_parallel_workers
    ) as executor:
      future_to_batch = {
        executor.submit(self.categorize, batch): batch
        for batch in _generate_batches(texts, batch_size)
      }
      for future in futures.as_completed(future_to_batch):
        if result := future.result():
          reports.append(result)
    return functools.reduce(operator.add, reports)

  def _safe_invoke_chain(self, text: str) -> dict[str, str]:
    try:
      result = self.chain.invoke(text)
    except langchain_exceptions.OutputParserException:
      return {text: 'FAILED_TO_PARSE_RESPONSE'}
    if isinstance(result, Mapping) and 'category' in result:
      return result
    return {text: 'FAILED_TO_CATEGORIZE'}


def _generate_batches(
  texts: Sequence[str], batch_size: int
) -> Generator[list[str], None, None]:
  """Produces subset of texts based on batch_size.

  Args:
    texts: All texts to be categorized.
    batch_size: How many texts should be taken in for categorization.

  Yield:
    Subset of texts.
  """
  i = 0
  while batch := list(itertools.islice(texts, i, i + batch_size)):
    yield batch
    i += batch_size
