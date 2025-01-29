# Copyright 2025 Google LLC
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

# pylint: disable=C0330, g-bad-import-order, g-multiple-import

"""Module for defining ORM models and repositories."""

import abc
from collections.abc import Sequence

import sqlalchemy

from creative_assistant.models import entity


class BaseRepository(abc.ABC):
  """Interface for defining repositories."""

  @abc.abstractmethod
  def get_by_id(self, identifier: str) -> entity.Entity | None:
    """Specifies get operations."""

  @abc.abstractmethod
  def add(
    self,
    results: entity.Entity | Sequence[entity.Entity],
  ) -> None:
    """Specifies add operations."""

  def list(self) -> list[entity.Entity]:
    """Returns all entities from the repository."""
    return self.results


class SqlAlchemyRepository(BaseRepository):
  """Uses SqlAlchemy engine for persisting entities."""

  def __init__(
    self, db_url: str, orm_model: entity.Entity, primary_key: str
  ) -> None:
    """Initializes SqlAlchemyRepository."""
    self.db_url = db_url
    self.orm_model = orm_model
    self.primary_key = primary_key
    self.initialized = False

  def initialize(self) -> None:
    """Creates all ORM objects."""
    entity.Entity.metadata.create_all(self.engine)
    self.initialized = True

  @property
  def session(self) -> sqlalchemy.orm.sessionmaker[sqlalchemy.orm.Session]:
    """Property for initializing session."""
    if not self.initialized:
      self.initialize()
    return sqlalchemy.orm.sessionmaker(bind=self.engine)

  @property
  def engine(self) -> sqlalchemy.engine.Engine:
    """Initialized SQLalchemy engine."""
    return sqlalchemy.create_engine(self.db_url)

  def get_by_id(self, identifier: str) -> entity.Entity | None:
    """Specifies get operations."""
    return (
      self.session()
      .query(self.orm_model)
      .filter_by(**{self.primary_key: identifier})
      .one_or_none()
    )

  def add(
    self,
    results: entity.Entity | Sequence[entity.Entity],
  ) -> None:
    """Specifies add operations."""
    if not isinstance(results, Sequence):
      results = [results]
    with self.session() as session:
      for result in results:
        session.add(result)
      session.commit()

  def list(self, limit: int | None = None) -> list[entity.Entity]:
    """Returns all tagging results from the repository."""
    query = (
      self.session()
      .query(self.orm_model)
      .order_by(self.orm_model.created_at.desc())
    )
    if limit:
      query = query.limit(limit)
    return query.all()

  def delete_by_id(self, identifier: str) -> None:
    """Specifies delete operations."""
    return (
      self.session()
      .query(self.orm_model)
      .filter_by(**{self.primary_key: identifier})
      .delete()
    )
