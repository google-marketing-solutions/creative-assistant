# Text Categorizer

## Problem statement

When analyzing texts of any nature (being search keywords and YouTube video
descriptions) it might be challenging to identify insights given unstructured
nature of such texts.

## Solution

`text-categorizer` uses power of large language models to perform categorization
at your texts - simply provide a couple of seed examples and `text-categorizer`
will do the rest.

## Deliverable (implementation)

`text-categorizer` is implemented as a:

* **library** - Use it in your projects with a help of `TextCategorizer` class.
* **CLI tool** - `text-categorizer` tool is available to be used in the terminal.
* **HTTP endpoint** - `text-categorizer` can be easily exposed as HTTP endpoint.
* **Langchain tool**  - integrated `text-categorizer` into your Langchain applications.

## Deployment

### Prerequisites

- Python 3.11+
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
* [API key](https://support.google.com/googleapi/answer/6158862?hl=en) to access to access Google Gemini.
  - Once you created API key export it as an environmental variable

    ```
    export GOOGLE_API_KEY=<YOUR_API_KEY_HERE>
    ```


### Installation

Install `text-categorizer` with `pip install text-categorization` command.

### Usage

> This section is focused on using `text-categorizer` as a CLI tool.
> Check [library](docs/how-to-use-text-categorizer-as-a-library.md),
> [http endpoint](docs/how-to-use-text-categorizer-as-a-http-endpoint.md),
> [langchain tool](docs/how-to-use-text-categorizer-as-a-langchain-tool.md)
> sections to learn more.

Once `text-categorizer` is installed you can call it:

```
text-categorizer 'text1' 'text2' 'text3' \
  --examples path/to/examples.txt \
  --llm gemini \
  --llm.model=gemini-1.5-flash \
  --output-type csv \
  --output-destination sample_results
```
where:

* `'text1' 'text2' 'text3'` - texts that needed to be categorized,
*  `--examples path/to/examples.txt` - path to examples (each line of the file
   should be formatted as *text* - *category*, i.e. *dog - pet*).
*  `--llm gemini` - type of large language model (currently only Google Gemini is supported)
*  `--llm.model=gemini-1.5-flash` - any parameters to initialize selected LLM
* `--output-type csv` - type of output
* `--output-destination sample_results` - name of output table or file.

`--examples` - might also come from BigQuery - simply pass full table name
  (project.dataset.table) as an example (Table should contains two columns -
  *text* and *category*).

Instead of passing texts as a parameters to `text-categorizer` you can provide
`--remote-texts` flag - it will accept a full table name in BigQuery. You can combine
passing texts and `--remote-texts` (Table should contain a column named *text*) .

## Disclaimer
This is not an officially supported Google product.
