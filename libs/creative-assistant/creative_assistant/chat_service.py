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

"""Specifies services to interact with saves chats."""

import uuid

from creative_assistant import repositories
from creative_assistant.models import chat as ch


class ChatRepository(repositories.SqlAlchemyRepository):
  """Repository for storing chats."""

  def __init__(self, db_url) -> None:
    """Initializes ChatRepository."""
    super().__init__(db_url, orm_model=ch.Chat, primary_key='chat_id')


class MessageRepository(repositories.SqlAlchemyRepository):
  """Repository for storing messages."""

  def __init__(self, db_url) -> None:
    """Initializes MessageRepository."""
    super().__init__(db_url, orm_model=ch.Message, primary_key='message_id')


class ChatService:
  """Handlers interaction with chats."""

  def __init__(self, chat_repository: ChatRepository | None = None) -> None:
    """Initializes ChatService."""
    if not chat_repository:
      chat_repository = ChatRepository(db_url='sqlite:///test2.db')
    self.repo = chat_repository
    self.message_repository = MessageRepository(db_url=self.repo.db_url)

  def get_chats(self, limit: int = 10, offset: int = 0) -> list[ch.Chat]:
    """Returns available chats.

    Args:
      limit: Number of chats to return.
      offset: Offset for loading extra chats.

    Returns:
      Chats without their messages.
    """
    return [
      ch.Chat(chat_id=c.chat_id, name=c.name, created_at=c.created_at)
      for c in self.repo.list(limit, offset)
    ]

  def load_chat(self, chat_id: str) -> ch.Chat | None:
    """Loads chat by its id."""
    if isinstance(chat_id, str):
      chat_id = uuid.UUID(chat_id)
    return self.repo.get_by_id(chat_id)

  def save_chat(self, chat: ch.Chat) -> str:
    """Saves chat to repository."""
    chat_id = chat.chat_id
    self.repo.add(chat)
    return chat_id

  def save_message(self, message: ch.Message) -> None:
    """Saves message to repository."""
    self.message_repository.add(message)

  def delete_chat(self, chat_id: str) -> None:
    """Deletes chat from repository."""
    self.repo.delete_by_id(uuid.UUID(chat_id))

  def rename_chat(self, chat_id: str, name: str) -> None:
    """Renames chat."""
    return self.repo.update(uuid.UUID(chat_id), {'name': name})
