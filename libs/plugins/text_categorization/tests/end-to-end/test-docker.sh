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
source .env
docker run \
  -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
  -v $APPLICATION_DEFAULT_CREDENTIALS:/app/service_account.json \
  wl-cat-dev2 \
  --remote-texts $TEXT_TABLE \
  --examples $EXAMPLES_TABLE \
  --llm gemini \
  --llm.model=gemini-1.5-flash \
  --output-type bq \
  --output-destination result \
  --bq.project=$BQ_PROJECT \
  --bq.dataset=$BQ_DATASET
