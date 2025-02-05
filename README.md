# Creative Assistant

## Problem statement

Having information information scattered across multiple places makes it
time-consuming to generate insight needed to come up with new creative
concepts.

## Solution

Creative Assistant uses power of large language models to organize information
available in multiple places and provide a chat bot interface to answer common
question regarding user personas, current creative and audience trends and more.

## Deliverable (implementation)

Creative Assistant is implemented as a:

* **CLI** - Creative Assistant can be easily exposed as CLI tool.
* **HTTP endpoint** - Creative Assistant can be easily exposed as HTTP endpoint.

## Deployment

### Prerequisites

- Python 3.8+
- A GCP project with billing account attached
- [Service account](https://cloud.google.com/iam/docs/creating-managing-service-accounts#creating)
  created and [service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating)
  downloaded in order to write data to BigQuery.

  - Once you downloaded service account key export it as an environmental variable

    ```
    export GOOGLE_APPLICATION_CREDENTIALS=path/to/service_account.json
    ```

  - If authenticating via service account is not possible you can authenticate with the following command:
    ```
    gcloud auth application-default login
    ```

### Installation

1. Install dependencies for Creative Assistant:
```
pip install creative-assistant
```

2. Expose necessary environmental variables to ensure correct initialization
of Creative Assistant:

```
export LLM_TYPE=gemini
export LLM_MODEL=gemini-1.5-flash
export CLOUD_PROJECT=<YOUR_GOOGLE_CLOUD_PROJECT_HERE>
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export ASSISTANT_LOG_FILE=path/to/assistant.log
```

### Usage

Once dependencies for Creative Assistant are installed you can run the following command:

```
creative-assistant
```

Now you can interact with assistant by asking it various question.
To end conversation enter `quit`, `bye` or `exit` as a message.

> You can launch web version of Creative Assistant by running the following command:
> `uvicorn creative_assistant.entrypoints.server:app`

## Disclaimer
This is not an officially supported Google product. This project is not
eligible for the [Google Open Source Software Vulnerability Rewards
Program](https://bughunters.google.com/open-source-security).
