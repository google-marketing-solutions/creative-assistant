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
"""Streamlit entrypoint for running creative assistant."""

# pylint: disable=C0330, g-bad-import-order, g-multiple-import

import collections
import datetime
import json
import os
import pathlib
import re
import uuid
from typing import Final

import dotenv
import streamlit as st

from creative_assistant import assistant, logger

CHATS_LOCATION: Final[str] = os.getenv(
  'CREATIVE_ASSISTANT_CHAT_FOLDER', pathlib.Path(__file__).parent / 'chats.json'
)


def load_chats() -> None:
  """Loads all saved chats into session_state."""
  try:
    with pathlib.Path.open(CHATS_LOCATION, 'r', encoding='utf-8') as f:
      chats = json.load(f)

      st.session_state.messages = collections.defaultdict(list)
      st.session_state.messages.update(chats)
  except FileNotFoundError:
    st.session_state.messages = collections.defaultdict(list)


def save_chats() -> None:
  """Saves messages from session_state to json."""
  with pathlib.Path.open(CHATS_LOCATION, 'w', encoding='utf-8') as f:
    json.dump(st.session_state.messages, f)


def extract_media_links(response: str) -> list[tuple[str, str]]:
  """Extracts links for media from LLM response."""
  results = []
  regexp = r'(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+'
  if found_urls := re.findall(regexp, response):
    for url in found_urls:
      if url.endswith('.jpg'):
        results.append(('image', url))
      elif url.endswith('.mp4') or 'youtube' in url or 'youtu.be' in url:
        results.append(('video', url))
  return results


def reset_chat_settings() -> None:
  """Resets session state."""
  st.session_state.prompt_id = ''


dotenv.load_dotenv()
load_chats()

st.set_page_config(page_title='Creative Assistant', layout='wide')
st.title('Creative Assistant')

if 'session_id' not in st.session_state:
  st.session_state.session_id = str(uuid.uuid1())
if 'assistant' not in st.session_state:
  creative_assistant = assistant.bootstrap_assistant()
  creative_assistant.start_chat(st.session_state.session_id)
  st.session_state.assistant = creative_assistant
if 'logger' not in st.session_state:
  st.session_state.logger = logger.init_logging('streamlit assistant')
if 'messages' not in st.session_state:
  st.session_state.messages = collections.defaultdict(list)
if 'prompt_id' not in st.session_state:
  st.session_state.prompt_id = ''
if 'new_chat' not in st.session_state:
  st.session_state.new_chat = False
if 'toasted' not in st.session_state:
  st.session_state.toasted = False


creative_assistant = st.session_state.assistant
assistant_logger = st.session_state.logger
session_id = st.session_state.session_id or str(uuid.uuid1())


def handle_assistant(chat_id: str):
  """Handles all interaction with assistant within a single chat_id."""
  for chat, messages in st.session_state.messages.items():
    if chat == chat_id:
      for message in messages:
        with st.chat_message(message['role']):
          st.markdown(message['content'])

  if text := st.chat_input('Enter your question'):
    st.chat_message('user').markdown(text)
    result = creative_assistant.interact(text)
    for media_type, media_url in extract_media_links(result.input):
      if media_type == 'image':
        st.chat_message('user').image(media_url)
      if media_type == 'video':
        st.chat_message('user').video(media_url)

    user_message, assistant_message = result.to_chat_messages()
    st.session_state.messages[chat_id].append(user_message)
    st.session_state.messages[chat_id].append(assistant_message)
    with st.chat_message('assistant'):
      st.markdown(result.output)
      assistant_logger.info(
        '[Session: %s, Prompt: %s]: Message: %s',
        result.chat_id,
        result.prompt_id,
        {'input': result.input, 'output': result.output},
      )
      st.session_state.prompt_id = result.prompt_id
    save_chats()

  if prompt_id := st.session_state.prompt_id:
    feedback = st.feedback(key=prompt_id)
    if feedback is not None:
      assistant_logger.info(
        '[Session: %s, Prompt: %s]: Feedback: %d',
        session_id,
        prompt_id,
        feedback,
      )


def new_chat() -> str:
  """Creates new chat."""
  chat_id = str(uuid.uuid1())
  creative_assistant.resume_chat(chat_id)
  if not st.session_state.toasted:
    st.toast(f'Started new chat {chat_id}')
    st.session_state.toasted = True
  reset_chat_settings()
  st.session_state.messages[chat_id] = []
  st.session_state.new_chat = True
  save_chats()
  return chat_id


def load_chat() -> str | None:
  """Resumes selected chat."""
  option = st.selectbox(
    'Available chats',
    chat_ids_to_names.keys(),
    index=None,
    placeholder='Select a chat',
  )
  if not st.session_state.new_chat and (
    chat_id := chat_ids_to_names.get(option)
  ):
    creative_assistant.resume_chat(chat_id)
    st.session_state.session_id = chat_id
    st.session_state.new_chat = False
    if not st.session_state.toasted:
      st.toast(f'Loading chat {chat_id}')
      st.session_state.toasted = True
    return chat_id
  return None


def default_chat() -> str:
  """Starts chat with session generated chat_id."""
  chat_id = st.session_state.session_id
  if not st.session_state.toasted:
    st.toast(f'Starting default chat {chat_id}')
    st.session_state.toasted = True
  return chat_id


def convert_chat_id_to_name(chat_id: str) -> str:
  """Converts chat_id to human readable chat name."""
  chat_date_time = datetime.datetime.fromtimestamp(
    (uuid.UUID(chat_id).time - 0x01B21DD213814000) * 100 / 1e9
  ).strftime('%Y-%m-%d %H-%M')
  return f'Chat at {chat_date_time}'


with st.sidebar:
  chat_ids_to_names = {
    convert_chat_id_to_name(chat_id): chat_id
    for chat_id, chat_content in st.session_state.messages.items()
    if chat_content
  }
  if st.button('+New chat'):
    selected_chat_id = new_chat()
    if loaded_chat := load_chat():
      selected_chat_id = loaded_chat
  elif (
    chat_ids_to_names
    and not (selected_chat_id := load_chat())
    and not st.session_state.new_chat
  ):
    selected_chat_id = default_chat()
  else:
    selected_chat_id = default_chat()

handle_assistant(selected_chat_id)
