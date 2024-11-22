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
"""Helper module for logging initialization."""

# pylint: disable=C0330, g-bad-import-order, g-multiple-import

import logging
import os


def init_logging(logger_name: str):
  """Helper function to initialize logging."""
  loglevel = os.environ.get('ASSISTANT_LOG_LEVEL', 'WARNING')
  logging.basicConfig(
    format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
    level=loglevel,
    datefmt='%Y-%m-%d %H:%M:%S',
  )
  logger = logging.getLogger(logger_name)
  if logfile := os.environ.get('ASSISTANT_LOG_FILE'):
    file_handler = logging.FileHandler(logfile)
    file_handler.setLevel(loglevel)
    formatter = logging.Formatter(
      '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
  logger.propagate = True
  return logger
