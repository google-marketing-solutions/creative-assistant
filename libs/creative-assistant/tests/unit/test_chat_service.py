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

# pylint: disable=C0330, g-bad-import-order, g-multiple-import, missing-class-docstring, missing-module-docstring

import creative_assistant
import pytest
from creative_assistant import chat_service


class TestChatService:
  @pytest.fixture(scope='class')
  def test_db(self, tmp_path_factory):
    return tmp_path_factory.mktemp('data') / 'test.db'

  @pytest.fixture(scope='class')
  def service(self, test_db):
    repo = chat_service.ChatRepository(f'sqlite:///{test_db}')
    return chat_service.ChatService(repo)

  @pytest.fixture(scope='class')
  def test_chat_id(self, service):
    new_chat = creative_assistant.Chat()
    return service.save_chat(new_chat)

  def test_get_chats_returns_all_chats(self, service, test_chat_id):
    chats = service.get_chats()
    expected_chat = creative_assistant.Chat(chat_id=test_chat_id, name='')
    assert chats[0] == expected_chat

  def test_add_message_saves_message_to_chat(self, service, test_chat_id):
    new_message = creative_assistant.Message(
      chat_id=test_chat_id, author='user', content='Test'
    )
    service.save_message(new_message)
    chat = service.load_chat(test_chat_id)
    expected_chat = creative_assistant.Chat(chat_id=test_chat_id, name='')
    assert chat == expected_chat
    assert chat.messages
