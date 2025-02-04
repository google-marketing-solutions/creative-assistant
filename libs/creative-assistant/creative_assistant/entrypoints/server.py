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
"""Provides HTTP endpoint for CreativeAssistant."""

# pylint: disable=C0330, g-bad-import-order, g-multiple-import

import dotenv
import fastapi
import pydantic

import creative_assistant
from creative_assistant import assistant, logger

dotenv.load_dotenv()

app = fastapi.FastAPI()

bootstraped_assistant = assistant.bootstrap_assistant()

assistant_logger = logger.init_logging('server')


class CreativeAssistantPostRequest(pydantic.BaseModel):
  """Specifies structure of request for interacting with assistant.

  Attributes:
    question: Question to the assistant.
    chat_id: Optional chat_id to resume conversation.
  """

  question: str
  chat_id: str | None = None


class CreativeAssistantChatPostRequest(pydantic.BaseModel):
  """Specifies structure of request for interacting with assistant.

  Attributes:
    chat_name: Name of a chat.
    chat_id: Optional chat_id.
  """

  name: str


@app.get('/api/tools')
def get_tools():
  return bootstraped_assistant.tools_info


@app.get('/api/chats')
def get_chats(limit: int = 5, offset: int = 0):
  return [
    chat.to_dict()
    for chat in bootstraped_assistant.chat_service.get_chats(limit, offset)
  ]


@app.post('/api/chats')
def create_chat(request: CreativeAssistantChatPostRequest) -> None:
  chat = creative_assistant.Chat(name=request.name)
  return bootstraped_assistant.chat_service.save_chat(chat)


@app.get('/api/chats/{chat_id}')
def get_chat(chat_id: str):
  return bootstraped_assistant.chat_service.load_chat(chat_id).to_full_dict()


@app.post('/api/interact')
def interact(
  request: CreativeAssistantPostRequest,
) -> str:
  """Interacts with CreativeAssistant.

  Args:
    request: Mapping with question to assistant.

  Returns:
    Question and answer to it.
  """
  result = bootstraped_assistant.interact(request.question, request.chat_id)
  assistant_logger.info(
    '[Session: %s, Prompt: %s]: Message: %s',
    result.chat_id,
    result.prompt_id,
    {'input': result.input, 'output': result.output},
  )
  return result.output
