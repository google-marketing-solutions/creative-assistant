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

import argparse
import pathlib

import fastapi
import pydantic
import uvicorn
from fastapi.staticfiles import StaticFiles
from pydantic_settings import BaseSettings
from typing_extensions import Annotated

import creative_assistant
from creative_assistant import assistant, logger


class CreativeAssistantSettings(BaseSettings):
  """Specifies environmental variables for creative assistant.

  Ensure that mandatory variables are exposed via
  export ENV_VARIABLE_NAME=VALUE.

  Attributes:
    no_tools: Whether assistant can run without tools.
  """

  tools: str = 'All'


app = fastapi.FastAPI()


class Dependencies:
  """Common dependencies for the app."""

  def __init__(self) -> None:
    """Initializes common dependencies."""
    settings = CreativeAssistantSettings()
    self.assistant = assistant.bootstrap_assistant(tools=settings.tools)
    self.logger = logger.init_logging('server')


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


class ChatUpdateFieldMask(pydantic.BaseModel):
  """Specifies supported fields for chat update."""

  name: str | None = None
  pinned: bool | None = None


@app.get('/api/tools')
def get_tools(  # noqa: D103
  dependencies: Annotated[Dependencies, fastapi.Depends(Dependencies)],
):
  return dependencies.assistant.tools_info


@app.get('/api/chats')
def get_chats(  # noqa: D103
  dependencies: Annotated[Dependencies, fastapi.Depends(Dependencies)],
  limit: int = 5,
  offset: int = 0,
):
  return [
    chat.to_dict()
    for chat in dependencies.assistant.chat_service.get_chats(limit, offset)
  ]


@app.post('/api/chats')
def create_chat(  # noqa: D103
  request: CreativeAssistantChatPostRequest,
  dependencies: Annotated[Dependencies, fastapi.Depends(Dependencies)],
) -> None:
  chat = creative_assistant.Chat(name=request.name)
  return dependencies.assistant.chat_service.save_chat(chat)


@app.get('/api/chats/{chat_id}')
def get_chat(  # noqa: D103
  chat_id: str,
  dependencies: Annotated[Dependencies, fastapi.Depends(Dependencies)],
):
  return dependencies.assistant.chat_service.load_chat(chat_id).to_full_dict()


@app.delete('/api/chats/{chat_id}')
def delete_chat(  # noqa: D103
  chat_id: str,
  dependencies: Annotated[Dependencies, fastapi.Depends(Dependencies)],
):
  dependencies.assistant.chat_service.delete_chat(chat_id)


@app.patch('/api/chats/{chat_id}', response_model=ChatUpdateFieldMask)
def update_chat(  # noqa: D103
  chat_id: str,
  updates: ChatUpdateFieldMask,
  dependencies: Annotated[Dependencies, fastapi.Depends(Dependencies)],
):
  update_data = {
    field: data for field, data in updates.dict().items() if data is not None
  }
  dependencies.assistant.chat_service.update_chat(chat_id, **update_data)


@app.post('/api/interact')
def interact(  # noqa: D103
  request: CreativeAssistantPostRequest,
  dependencies: Annotated[Dependencies, fastapi.Depends(Dependencies)],
) -> str:
  """Interacts with CreativeAssistant.

  Args:
    request: Mapping with question to assistant.
    dependencies: Common dependencies for the app.

  Returns:
    Question and answer to it.
  """
  result = dependencies.assistant.interact(request.question, request.chat_id)
  dependencies.logger.info(
    '[Session: %s, Prompt: %s]: Message: %s',
    result.chat_id,
    result.prompt_id,
    {'input': result.input, 'output': result.output},
  )
  return result.output


build_dir = pathlib.Path(pathlib.Path(__file__).parent / 'static/browser')
app.mount(
  '/',
  StaticFiles(
    directory=build_dir,
    html=True,
  ),
  name='static',
)


def main():  # noqa: D103
  parser = argparse.ArgumentParser()
  parser.add_argument(
    '--port',
    dest='port',
    default='8000',
    type=int,
    help='Port to launch CreativeAssistant Server',
  )
  args = parser.parse_args()
  uvicorn.run(app, host='0.0.0.0', port=args.port)


if __name__ == '__main__':
  main()
