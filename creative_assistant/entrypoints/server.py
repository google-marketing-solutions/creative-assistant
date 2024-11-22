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
from typing_extensions import TypedDict

from creative_assistant import assistant, logger

dotenv.load_dotenv()

app = fastapi.FastAPI()

creative_assistant = assistant.bootstrap_assistant()
chat_id = creative_assistant.start_chat()

assistant_logger = logger.init_logging('server')


class CreativeAssistantPostRequest(TypedDict):
  """Specifies structure of request for interacting with assistant.

  Attributes:
    question: Question to the assistant.
    chat_id: Optional chat_id to resume conversation.
  """

  question: str
  chat_id: str | None


@app.post('/')
def interact(
  request: CreativeAssistantPostRequest = fastapi.Body(embed=True),
) -> str:
  """Interacts with CreativeAssistant.

  Args:
    request: Mapping with question to assistant.

  Returns:
    Question and answer to it.
  """
  result = creative_assistant.interact(request.question, request.chat_id)
  assistant_logger.info(
    '[Session: %s, Prompt: %s]: Message: %s',
    result.chat_id,
    result.prompt_id,
    {'input': result.input, 'output': result.output},
  )
  return result.output
