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
"""Command line entry point for calling trend_analyzer."""

# pylint: disable=C0330, g-bad-import-order, g-multiple-import

import argparse
import sys
import uuid

import dotenv
from rich import console, prompt, text

from creative_assistant import assistant, logger


def main():  # noqa D103
  parser = argparse.ArgumentParser()
  parser.add_argument('question', nargs='*', help='Question to assistant')
  parser.add_argument(
    '--chat-id',
    dest='chat_id',
    default=str(uuid.uuid1()),
    help='Optional chat_id to resume conversation',
  )
  parser.add_argument(
    '--verbose',
    dest='verbose',
    action='store_true',
    help='Whether to provide debug info when running assistant',
  )
  parser.add_argument(
    '--no-tools',
    dest='no_tools',
    action='store_true',
    help='Whether to start assistant without tools',
  )

  args = parser.parse_args()
  dotenv.load_dotenv()
  assistant_logger = logger.init_logging('cli')

  creative_assistant = assistant.bootstrap_assistant(
    verbose=args.verbose, no_tools=args.no_tools
  )
  rich_console = console.Console()
  if args.question:
    result = creative_assistant.interact(args.question, args.chat_id)
    assistant_logger.info(
      '[Session: %s, Prompt: %s]: Message: %s',
      result.chat_id,
      result.prompt_id,
      {'input': result.input, 'output': result.output},
    )
    rich_console.print(text.Text(result.output))
  else:
    question = prompt.Prompt.ask('Enter your question')
    while question:
      result = creative_assistant.interact(question)
      assistant_logger.info(
        '[Session: %s, Prompt: %s]: Message: %s',
        result.chat_id,
        result.prompt_id,
        {'input': result.input, 'output': result.output},
      )
      rich_console.print(text.Text(result.output))
      question = prompt.Prompt.ask(text.Text('Enter your question'))
      if question.lower() in ('bye', 'quit', 'exit'):
        sys.exit()
      if 'new chat' in question.lower():
        creative_assistant.end_chat()
        chat_id = creative_assistant.start_chat()
        logger.info('[Assistant][CLI]: Started new chat %s', chat_id)


if __name__ == '__main__':
  main()
