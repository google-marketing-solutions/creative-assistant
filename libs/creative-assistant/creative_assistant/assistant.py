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
"""Module defining CreativeAssistant.

CreativeAssistant is responsible to interacting with various sources of
information related to creative trends.
"""

# pylint: disable=C0330, g-bad-import-order, g-multiple-import

from __future__ import annotations

import inspect
import os
import uuid
from collections.abc import Sequence
from importlib.metadata import entry_points

import langchain_core
import pydantic
from langchain import agents
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core import language_models, prompts

from creative_assistant import chat_service, llms
from creative_assistant.models import chat as ch

_SYSTEM_PROMPT = """You are a helpful assistant answering users' questions.
You have various tools in disposal and you can use them only when you 100% sure
that tool is the right choice.
When you used a tool always mention the tool's name in the response.
If no tool is used, indicate that the answer is coming directly from the LLM.
Here are the tools you have: {tools_descriptions}
"""


class CreativeAssistantResponse(pydantic.BaseModel):
  """Defines LLM response and its meta information.

  Attributes:
    input: Question to LLM.
    output: Response from LLM.
    chat_id: Unique chat identifier.
    prompt_id: Unique prompt identifier.
  """

  input: str
  output: str
  chat_id: str
  prompt_id: str = pydantic.Field(default_factory=lambda: str(uuid.uuid1()))

  def to_chat_messages(self) -> tuple[dict[str, str], dict[str, str]]:
    """Converts response to user / chat bot interaction."""
    return (
      {
        'role': 'user',
        'content': self.input,
        'chat_id': self.chat_id,
        'prompt_id': self.prompt_id,
      },
      {
        'role': 'assistant',
        'content': self.output,
        'chat_id': self.chat_id,
        'prompt_id': self.prompt_id,
      },
    )


class CreativeAssistant:
  """Helps with generating advertising creative ideas.

  Attributes:
    llm: Instantiated LLM.
    tools: Various tools used to question external sources.
    verbose: Whether to provide debug information when running assistant.
    chat_service: Service for handling chat history.
  """

  def __init__(
    self,
    llm: language_models.BaseLanguageModel,
    tools: Sequence[langchain_core.tools.BaseTool],
    verbose: bool = False,
    chats_service: chat_service.ChatService = chat_service.ChatService(),
  ) -> None:
    """Initializes CreativeAssistant based on LLM and vectorstore.

    Args:
      llm: Instantiated LLM.
      tools: Various tools used to question external sources.
      verbose: Whether to provide debug information when running assistant.
      chats_service: Service for handling chat history.
    """
    self.llm = llm
    self.tools = tools
    self.verbose = verbose
    self.chat_service = chats_service

  @property
  def tools_descriptions(self) -> dict[str, str]:
    """Mapping between tool's name and its description."""
    return {tool.name: tool.description for tool in self.tools}

  @property
  def tools_info(self) -> dict[str, dict[str, str | list[str]]]:
    """Mapping between tool name and it's description and built-in prompts."""
    return {
      tool.name: {
        'description': tool.description,
        'prompts': tool.pre_prompts if hasattr(tool, 'pre_prompts') else [],
      }
      for tool in self.tools
    }

  @property
  def agent_executor(self) -> agents.AgentExecutor:
    """Defines agent executor to handle question from users."""
    tools_descriptions = '\n'.join(
      [
        f'{name}: {description}'
        for name, description in self.tools_descriptions.items()
      ]
    )

    prompt = prompts.ChatPromptTemplate(
      messages=[
        prompts.SystemMessagePromptTemplate(
          prompt=prompts.PromptTemplate(
            input_variables=[],
            template=_SYSTEM_PROMPT.format(
              tools_descriptions=tools_descriptions
            ),
          )
        ),
        prompts.MessagesPlaceholder(
          variable_name='chat_history', optional=True
        ),
        prompts.HumanMessagePromptTemplate(
          prompt=prompts.PromptTemplate(
            input_variables=['input'], template='{input}'
          )
        ),
        prompts.MessagesPlaceholder(variable_name='agent_scratchpad'),
      ]
    )

    agent = agents.create_tool_calling_agent(self.llm, self.tools, prompt)
    return langchain_core.runnables.history.RunnableWithMessageHistory(
      agents.AgentExecutor(agent=agent, tools=self.tools, verbose=self.verbose),
      _get_session_history,
      input_messages_key='input',
      history_messages_key='chat_history',
    )

  def interact(
    self, question: str, chat_id: str | None = None
  ) -> CreativeAssistantResponse:
    """Handles question from users.

    Args:
      question: Any question user might have to CreativeAssistant.
      chat_id: Identifier of chat with historical messages.

    Returns:
      Mappings with question and answer.
    """
    create_chat_name = False
    if not chat_id:
      chat_id = self.chat_service.save_chat(ch.Chat())
      create_chat_name = True
    if isinstance(chat_id, str):
      chat_id = uuid.UUID(chat_id)
    if not self.chat_service.load_chat(chat_id):
      self.chat_service.save_chat(ch.Chat(chat_id=chat_id))
      create_chat_name = True
    new_message = ch.Message(chat_id=chat_id, author='user', content=question)
    self.chat_service.save_message(new_message)
    if create_chat_name:
      self._name_chat(chat_id, question)

    response = self.agent_executor.invoke(
      {'input': question},
      config={'configurable': {'session_id': chat_id.hex}},
    )
    self.chat_service.save_message(
      ch.Message(
        chat_id=chat_id, author='assistant', content=response.get('output')
      )
    )
    return CreativeAssistantResponse(
      input=response.get('input'),
      output=response.get('output'),
      chat_id=chat_id.hex,
    )

  def _name_chat(self, chat_id: str, initial_message: str) -> str:
    try:
      llm_response = self.llm.invoke(
        'Give a short summary (maximum 30 characters) of the following '
        f'question: {initial_message}'
      )
      chat_name = llm_response.content.strip()
    except Exception:
      chat_name = ''
    self.chat_service.rename_chat(chat_id, chat_name)


def bootstrap_assistant(
  parameters: dict[str, str | int | float] | None = None,
  verbose: bool = False,
  no_tools: bool = False,
) -> CreativeAssistant:
  """Builds CreativeAssistant with injected tools.

  Args:
    parameters:  Parameters for assistant and its tools instantiation.
    verbose: Whether to display additional logging information.
    no_tools: Whether assistant can start without any tools.

  Returns:
    Assistant with injected tools.

  Raises:
    CreativeAssistantError: If no tools are found during the bootstrap.
  """
  if not parameters:
    parameters = {}
  base_llm_parameters = {
    'llm_type': os.getenv('LLM_TYPE', llms.DEFAULT_LLM_TYPE),
    'llm_parameters': {
      'model': os.getenv('LLM_MODEL', llms.DEFAULT_LLM_MODEL),
      'project': os.getenv('CLOUD_PROJECT'),
      'temperature': 0.2,
    },
  }
  tool_parameters = {**base_llm_parameters, **parameters, 'verbose': verbose}

  if no_tools:
    tools = []
  elif not (tools := _bootstrap_tools(tool_parameters)):
    raise CreativeAssistantError('No Creative Assistant tools found.')

  return CreativeAssistant(
    llm=llms.create_llm(**base_llm_parameters),
    tools=tools,
    verbose=verbose,
  )


def _get_session_history(session_id):
  return SQLChatMessageHistory(session_id, 'sqlite:///memory.db')


def _bootstrap_tools(
  parameters: dict[str, str | dict[str, str | float]],
) -> list[langchain_core.tools.BaseTool]:
  """Instantiates tools modules.

  Args:
    parameters:  Common parameters for tool instantiation.

  Returns:
    Assistant with injected tools.
  """
  tools = entry_points(group='creative_assistant')
  injected_tools = []
  for tool in tools:
    try:
      tool_module = tool.load()
      for name, obj in inspect.getmembers(tool_module):
        if inspect.isclass(obj) and issubclass(
          obj, langchain_core.tools.BaseTool
        ):
          injected_tools.append(getattr(tool_module, name)(**parameters))
    except ModuleNotFoundError:
      continue
  return injected_tools


class CreativeAssistantChatError(Exception):
  """Chat specific exception."""


class CreativeAssistantError(Exception):
  """Assistant specific exception."""
