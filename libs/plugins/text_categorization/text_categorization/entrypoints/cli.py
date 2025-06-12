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
"""Provides CLI for text categorization."""

import argparse
import operator
import pathlib

import smart_open
from garf_executors import bq_executor
from garf_executors.entrypoints import utils as garf_utils
from garf_io import writer
from google.api_core import exceptions as google_api_exceptions

from text_categorization import categorizer, llms, vectorstore


def read_examples(path: str | pathlib.Path) -> list[str]:
  """Reads examples of categorization from provided path.

  Args:
    path: Relative path to file with examples.

  Returns:
    Multiple example to help with categorization.
  """
  with smart_open.open(
    pathlib.Path(__file__).resolve().parent / path,
    'r',
    encoding='utf-8',
  ) as f:
    return f.readlines()


def read_example_from_bq(
  table_name: str, subcategory_needed: bool = False
) -> list[str]:
  """Reads examples of categorization from BigQuery.

  Example table should contains two columns (text and category).

  Args:
    table_name: Fully qualified table name (project_id.dataset.table).
    subcategory_needed: Whether to read subcategory from examples.

  Returns:
    Multiple example to help with categorization.
  """
  project_id, *dataset_table = table_name.split('.')
  table_name = '.'.join(dataset_table)
  fields = ['text', 'category']
  if subcategory_needed:
    fields.append('subcategory')
  query_text = f'SELECT {", ".join(fields)} FROM {table_name};'
  examples = bq_executor.BigQueryExecutor(project_id).execute(
    'examples', query_text
  )
  field_getter = operator.attrgetter(*fields)
  return [' - '.join(field_getter(data)) for data in examples.itertuples()]


def read_texts_from_bq(table_name: str) -> list[str]:
  """Reads texts for categorization from BigQuery.

  Table should contains one column called `text`.

  Args:
    table_name: Fully qualified table name (project_id.dataset.table).

  Returns:
    Texts for categorization.
  """
  project_id, *dataset_table = table_name.split('.')
  table_name = '.'.join(dataset_table)
  query_text = f'SELECT text FROM {table_name};'
  texts = bq_executor.BigQueryExecutor(project_id).execute('texts', query_text)
  return [data.text for data in texts.itertuples()]


def main():  # noqa D103
  parser = argparse.ArgumentParser()
  parser.add_argument('texts', nargs='*')
  parser.add_argument('--llm', dest='llm')
  parser.add_argument('--output-type', dest='output', default='console')
  parser.add_argument(
    '--output-destination', dest='destination', default='results'
  )
  parser.add_argument(
    '--remote-texts',
    dest='remote_texts',
    default=None,
  )
  parser.add_argument('--examples', dest='examples', default=None)
  parser.add_argument(
    '--examples-to-vectorstore',
    dest='examples_to_vectorstore',
    action='store_true',
  )
  parser.add_argument(
    '--subcategory-needed', dest='subcategory', action='store_true'
  )

  parser.add_argument('--max-workers', dest='max_workers', type=int, default=10)
  parser.add_argument('--batch-size', dest='batch_size', type=int, default=100)
  args, kwargs = parser.parse_known_args()
  params = garf_utils.ParamsParser(['llm', args.output]).parse(kwargs)

  if not args.examples:
    examples = None
  else:
    try:
      examples = read_example_from_bq(args.examples, args.subcategory)
    except (
      bq_executor.BigQueryExecutorError,
      google_api_exceptions.BadRequest,
      google_api_exceptions.NotFound,
    ):
      examples = read_examples(args.examples)

  if remote_texts := args.remote_texts:
    texts = read_texts_from_bq(remote_texts)
  else:
    texts = []

  llm = llms.create_categorizer_llm(args.llm, params.get('llm'))
  if examples_to_vectorstore := args.examples_to_vectorstore:
    vect_store = vectorstore.get_vector_store()
  else:
    vect_store = None
  text_categorizer = categorizer.TextCategorizer(
    llm=llm,
    vect_store=vect_store,
    subcategory_needed=args.subcategory,
  )

  if examples:
    text_categorizer.add_examples(
      examples, load_to_vectorstore=examples_to_vectorstore
    )
  result = text_categorizer.categorize(
    texts=args.texts + texts,
    max_parallel_workers=args.max_workers,
    batch_size=args.batch_size,
  )
  writer.create_writer(args.output, **params.get(args.output)).write(
    result, args.destination
  )


if __name__ == '__main__':
  main()
