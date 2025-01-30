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

"""Specifies chat related models used in Creative Assistant."""

from __future__ import annotations

import datetime
import uuid

import sqlalchemy
from creative_assistant.models import entity
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Message(entity.Entity):
  """Single interaction with CreativeAssistant.

  Message can be user or assistant generated.
  """

  __tablename__ = 'messages'

  chat_id: Mapped[uuid.UUID] = mapped_column(
    sqlalchemy.ForeignKey('chats.chat_id')
  )

  author: Mapped[str] = mapped_column(sqlalchemy.String(255))
  content: Mapped[str] = mapped_column(sqlalchemy.String(255))
  message_id: Mapped[uuid.UUID] = mapped_column(
    sqlalchemy.UUID,
    primary_key=True,
    default_factory=uuid.uuid4,
    unique=True,
  )
  created_at: Mapped[datetime.datetime] = mapped_column(
    sqlalchemy.DateTime, default_factory=datetime.datetime.utcnow
  )
  chat: Mapped[Chat] = relationship(back_populates='messages', init=False)

  def __repr__(self):
    return (
      f'Message(chat_id={self.chat_id}, author={self.author}, '
      f'message_id={self.message_id}, created_at={self.created_at})'
    )

  def to_dict(self) -> dict[str, str | datetime.datetime]:
    return {
      'author': self.author,
      'content': self.content,
      'created_at': self.created_at,
    }


class Chat(entity.Entity):
  """Represents series of interaction with CreativeAssistant.

  All the interactions are connected to the same context.
  """

  __tablename__ = 'chats'

  messages: Mapped[list[Message]] = relationship(
    back_populates='chat',
    init=False,
    lazy='selectin',
    default_factory=list,
  )
  chat_id: Mapped[uuid.UUID] = mapped_column(
    sqlalchemy.UUID,
    primary_key=True,
    unique=True,
    default_factory=uuid.uuid4,
  )
  name: Mapped[str] = mapped_column(sqlalchemy.String(255), default='')
  created_at: Mapped[datetime.datetime] = mapped_column(
    sqlalchemy.DateTime, default_factory=datetime.datetime.utcnow
  )

  def __repr__(self):
    return (
      f'Chat(chat_id={self.chat_id}, name={self.name}, '
      f'created_at={self.created_at})'
    )

  def __eq__(self, other: Chat) -> bool:
    return (self.chat_id, self.name) == (other.chat_id, other.name)

  def to_dict(self) -> dict[str, str | datetime.datetime]:
    return {
      'chat_id': self.chat_id.hex,
      'name': self.name,
      'created_at': self.created_at,
    }

  def to_full_dict(self) -> dict[str, str | datetime.datetime]:
    chat_info = self.to_dict()
    messages = [
      message.to_dict()
      for message in sorted(self.messages, key=lambda x: x.created_at)
    ]
    chat_info['messages'] = messages
    return chat_info
