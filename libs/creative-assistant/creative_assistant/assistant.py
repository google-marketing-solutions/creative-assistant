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

import dataclasses
import inspect
import logging
import os
import uuid
from collections.abc import Sequence
from importlib.metadata import entry_points

import langchain_core
from langchain import agents
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core import language_models, prompts

from creative_assistant import llms

_SYSTEM_PROMPT = """You are a helpful assistant answering users' questions.
You have various tools in disposal and you can use them only when you 100% sure
that tool is the right choice.
When you used a tool always mention the tool's name in the response.
If no tool is used, indicate that the answer is coming directly from the LLM.
Here are the tools you have: {tools_descriptions}
"""


@dataclasses.dataclass
class CreativeAssistantResponse:
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
  prompt_id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid1()))

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
  """

  def __init__(
    self,
    llm: language_models.BaseLanguageModel,
    tools: Sequence[langchain_core.tools.BaseTool],
    verbose: bool = False,
  ) -> None:
    """Initializes CreativeAssistant based on LLM and vectorstore.

    Args:
      llm: Instantiated LLM.
      tools: Various tools used to question external sources.
      verbose: Whether to provide debug information when running assistant.
    """
    self.llm = llm
    self.tools = tools
    self.verbose = verbose
    self._chat_id = None

  @property
  def tools_descriptions(self) -> dict[str, str]:
    """Mapping between tool's name and its description."""
    return {tool.name: tool.description for tool in self.tools}

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

  def start_chat(self, chat_id: str = str(uuid.uuid1())) -> str:
    """Attaches all CreativeAssistant interactions to a single chat session.

    Args:
      chat_id: Optional identifier of a chat.

    Returns:
      Generated or supplied chat_id.

    Raises:
      CreativeAssistantChatError: Raised when chat already started.
    """
    if self._chat_id is not None:
      raise CreativeAssistantChatError('Chat already started')
    self._chat_id = chat_id
    return chat_id

  def resume_chat(self, chat_id: str) -> None:
    """Instruct assistant to work only with selected chat.

    Args:
      chat_id: Identifier of a chat.
    """
    self._chat_id = chat_id

  def end_chat(self) -> None:
    """Stop mapping CreativeAssistant interactions to a single chat session."""
    if self._chat_id is None:
      logging.warning('No active chats')
    self._chat_id = None

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
    if chat_id is None and self._chat_id:
      chat_id = self._chat_id
    elif chat_id is None:
      chat_id = str(uuid.uuid1())

    response = self.agent_executor.invoke(
      {'input': question},
      config={'configurable': {'session_id': chat_id}},
    )
    return CreativeAssistantResponse(
      input=response.get('input'),
      output=response.get('output'),
      chat_id=chat_id,
    )


def bootstrap_assistant(
  parameters: dict[str, str | int | float] | None = None,
  verbose: bool = False,
) -> CreativeAssistant:
  """Builds CreativeAssistant with injected tools.

  Args:
    parameters:  Parameters for assistant and its tools instantiation.
    verbose: Whether to display additional logging information.

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

  if not (tools := _bootstrap_tools(tool_parameters)):
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
