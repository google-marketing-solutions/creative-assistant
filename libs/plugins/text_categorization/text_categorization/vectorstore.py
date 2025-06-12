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
"""Module for defining vector store.

Vectorstore contains necessary data to improve LLM results.
"""

import pathlib

import chromadb
import langchain_chroma
from langchain_core import embeddings, vectorstores


def get_vector_store(
  vectorstore_type: vectorstores.VectorStore = langchain_chroma.Chroma,
  vectorstore_directory: str | pathlib.Path | None = None,
  embedding_function: embeddings.Embeddings = embeddings.FakeEmbeddings(
    size=1300
  ),
) -> vectorstores.VectorStore:
  """Loads vectorestore.

  If path to vectorstore is not provided creates a simple vectorstore.

  Args:
    vectorstore_type: Type of vectorstore to be used.
    vectorstore_directory: Path to vectorstore.
    embedding_function: Function to generated embeddings in the vectorstore.

  Returns:
    Initialized vectorstore.
  """
  if not vectorstore_directory:
    return vectorstore_type(
      collection_name='categories', embedding_function=embedding_function
    )
  return vectorstore_type(
    persist_directory=vectorstore_directory,
    embedding_function=embedding_function,
    client_settings=chromadb.config.Settings(anonymized_telemetry=False),
  )


def format_docs(docs) -> str:
  """Formats documents from vectorstore to be used in a prompt."""
  return '\n\n'.join(doc.page_content for doc in docs)
