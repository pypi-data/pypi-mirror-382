<p align="center">
  <a href="https://arize.com/ax">
    <img src="https://storage.googleapis.com/arize-assets/arize-logo-white.jpg" width="600" />
  </a>
  <br/>
  <a target="_blank" href="https://pypi.org/project/arize/">
    <img src="https://img.shields.io/pypi/v/arize?color=blue">
  </a>
  <a target="_blank" href="https://pypi.org/project/arize/">
      <img src="https://img.shields.io/pypi/pyversions/arize">
  </a>
  <a target="_blank" href="https://arize-ai.slack.com/join/shared_invite/zt-2w57bhem8-hq24MB6u7yE_ZF_ilOYSBw#/shared-invite/email">
    <img src="https://img.shields.io/badge/slack-@arize-blue.svg?logo=slack">
  </a>
</p>

---

# Table of Contents <!-- omit in toc -->

- [Overview](#overview)
- [Key Features](#key-features)
- [Installation](#installation)
- [Usage](#usage)
  - [Instrumentation](#instrumentation)
  - [Operations on Spans](#operations-on-spans)
    - [Logging spans](#logging-spans)
    - [Update spans Evaluations, Annotations, and Metadata](#update-spans-evaluations-annotations-and-metadata)
    - [Exporting spans](#exporting-spans)
  - [Operations on ML Models](#operations-on-ml-models)
    - [Stream log ML Data for a Classification use-case](#stream-log-ml-data-for-a-classification-use-case)
    - [Log a batch of ML Data for a Object Detection use-case](#log-a-batch-of-ml-data-for-a-object-detection-use-case)
    - [Exporting ML Data](#exporting-ml-data)
  - [Generate embeddings for your data](#generate-embeddings-for-your-data)
  - [Operations on Datasets](#operations-on-datasets)
    - [List Datasets](#list-datasets)
    - [Create a Dataset](#create-a-dataset)
    - [Get Dataset by ID](#get-dataset-by-id)
    - [Delete a Dataset](#delete-a-dataset)
- [Configure Logging](#configure-logging)
  - [In Code](#in-code)
  - [Via Environment Variables](#via-environment-variables)
- [Community](#community)

# Overview

A helper package to interact with Arize AI APIs.

Arize is an AI engineering platform. It helps engineers develop, evaluate, and observe AI applications and agents. 

Arize has both Enterprise and OSS products to support this goal: 
- [Arize AX](https://arize.com/) — an enterprise AI engineering platform from development to production, with an embedded AI Copilot
- [Phoenix](https://github.com/Arize-ai/phoenix) — a lightweight, open-source project for tracing, prompt engineering, and evaluation
- [OpenInference](https://github.com/Arize-ai/openinference) — an open-source instrumentation package to trace LLM applications across models and frameworks

We log over 1 trillion inferences and spans, 10 million evaluation runs, and 2 million OSS downloads every month. 

# Key Features
- [**_Tracing_**](https://docs.arize.com/arize/observe/tracing) - Trace your LLM application's runtime using OpenTelemetry-based instrumentation.
- [**_Evaluation_**](https://docs.arize.com/arize/evaluate/online-evals) - Leverage LLMs to benchmark your application's performance using response and retrieval evals.
- [**_Datasets_**](https://docs.arize.com/arize/develop/datasets) - Create versioned datasets of examples for experimentation, evaluation, and fine-tuning.
- [**_Experiments_**](https://docs.arize.com/arize/develop/datasets-and-experiments) - Track and evaluate changes to prompts, LLMs, and retrieval.
- [**_Playground_**](https://docs.arize.com/arize/develop/prompt-playground)- Optimize prompts, compare models, adjust parameters, and replay traced LLM calls.
- [**_Prompt Management_**](https://docs.arize.com/arize/develop/prompt-hub)- Manage and test prompt changes systematically using version control, tagging, and experimentation.

# Installation

Install Arize (version 8 is currently under alpha release) via `pip` or `conda`:

```bash
pip install arize==8.0.0ax 
```
where `x` denotes the specific alpha release. Install the `arize-otel` package for auto-instrumentation of your LLM library:

```bash
pip install arize-otel
```

# Usage
  
## Instrumentation

See [arize-otel in PyPI](https://pypi.org/project/arize-otel/):

```python
from arize.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor

# Setup OpenTelemetry via our convenience function
tracer_provider = register(
    space_id=SPACE_ID,
    api_key=API_KEY,
    project_name="agents-cookbook",
)

# Start instrumentation
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
```

## Operations on Spans

Use `arize.spans` to interact with spans: log spans into Arize, update the span's evaluations, annotations and metadata in bulk. 

> **WARNING**: This is currently under an alpha release. Install with `pip install arize==8.0.0ax` where the `x` denotes the specific alpha version. Check the [pre-releases](https://pypi.org/project/arize/#history) page in PyPI.

### Logging spans

```python
from arize import ArizeClient

client = ArizeClient(api_key=API_KEY)
SPACE_ID = "<your-space-id>"
PROJECT_NAME = "<your-project-name>"

client.spans.log(
    space_id=SPACE_ID,
    project_name=PROJECT_NAME,
    dataframe=spans_df,
    # evals_df=evals_df, # Optionally pass the evaluations together with the spans
)
```

### Update spans Evaluations, Annotations, and Metadata

```python
from arize import ArizeClient

client = ArizeClient(api_key=API_KEY)
SPACE_ID = "<your-space-id>"
PROJECT_NAME = "<your-project-name>"

client.spans.update_evaluations(
    space_id=SPACE_ID,
    project_name=PROJECT_NAME,
    dataframe=evals_df,
    # force_http=... # Optionally pass force_http to update evaluations via HTTP instead of gRPC, defaults to False
)

client.spans.update_annotations(
    space_id=SPACE_ID,
    project_name=PROJECT_NAME,
    dataframe=annotations_df,
)

client.spans.update_metadata(
    space_id=SPACE_ID,
    project_name=PROJECT_NAME,
    dataframe=metadata_df,
)
```

### Exporting spans

Use the `export_to_df` or `export_to_parquet` to export large amounts of spans from Arize.

```python
from arize import ArizeClient
from datetime import datetime

FMT  = "%Y-%m-%d"
start_time = datetime.strptime("2024-01-01",FMT)
end_time = datetime.strptime("2026-01-01",FMT)

client = ArizeClient(api_key=API_KEY)
SPACE_ID = "<your-space-id>"
PROJECT_NAME = "<your-project-name>"

df = client.spans.export_to_df(
    space_id=SPACE_ID,
    project_name=PROJECT_NAME,
    start_time=start_time,
    end_time=end_time,
)
```

## Operations on ML Models

Use `arize.models` to interact with ML models: log ML data (traininv, validation, production) into Arize, either streaming or in batches.

> **WARNING**: This is currently under an alpha release. Install with `pip install arize==8.0.0ax` where the `x` denotes the specific alpha version. Check the [pre-releases](https://pypi.org/project/arize/#history) page in PyPI.

### Stream log ML Data for a Classification use-case

```python
from arize import ArizeClient
from arize.types import ModelTypes, Environments

client = ArizeClient(api_key=API_KEY)
SPACE_ID = "<your-space-id>"
MODEL_NAME = "<your-model-name>"

features=...
embedding_features=...

response = client.models.log_stream(
    space_id=SPACE_ID,
    model_name=MODEL_NAME,
    model_type=ModelTypes.SCORE_CATEGORICAL,
    environment=Environments.PRODUCTION,
    prediction_label=("not fraud",0.3),
    actual_label=("fraud",1.0),
    features=features,
    embedding_features=embedding_features,
)
```

### Log a batch of ML Data for a Object Detection use-case

```python
from arize import ArizeClient
from arize.types import ModelTypes, Environments

client = ArizeClient(api_key=API_KEY)
SPACE_ID = "<your-space-id>"
MODEL_NAME = "<your-model-name>"
MODEL_VERSION = "1.0"

from arize.types import Schema, EmbeddingColumnNames, ObjectDetectionColumnNames, ModelTypes, Environments

tags = ["drift_type"]
embedding_feature_column_names = {
    "image_embedding": EmbeddingColumnNames(
        vector_column_name="image_vector", link_to_data_column_name="url"
    )
}
object_detection_prediction_column_names = ObjectDetectionColumnNames(
    bounding_boxes_coordinates_column_name="prediction_bboxes",
    categories_column_name="prediction_categories",
    scores_column_name="prediction_scores",
)
object_detection_actual_column_names = ObjectDetectionColumnNames(
    bounding_boxes_coordinates_column_name="actual_bboxes",
    categories_column_name="actual_categories",
)

# Define a Schema() object for Arize to pick up data from the correct columns for logging
schema = Schema(
    prediction_id_column_name="prediction_id",
    timestamp_column_name="prediction_ts",
    tag_column_names=tags,
    embedding_feature_column_names=embedding_feature_column_names,
    object_detection_prediction_column_names=object_detection_prediction_column_names,
    object_detection_actual_column_names=object_detection_actual_column_names,
)

# Logging Production DataFrame
response = client.models.log_batch(
    space_id=SPACE_ID,
    model_name=MODEL_NAME,
    model_type=ModelTypes.OBJECT_DETECTION,
    dataframe=prod_df,
    schema=schema,
    environment=Environments.PRODUCTION,
    model_version = MODEL_VERSION, # Optionally pass a model version
)
```

### Exporting ML Data

Use the `export_to_df` or `export_to_parquet` to export large amounts of spans from Arize.

```python
from arize import ArizeClient
from datetime import datetime

FMT  = "%Y-%m-%d"
start_time = datetime.strptime("2024-01-01",FMT)
end_time = datetime.strptime("2026-01-01",FMT)

client = ArizeClient(api_key=API_KEY)
SPACE_ID = "<your-space-id>"
MODEL_NAME = "<your-model-name>"
MODEL_VERSION = "1.0"

df = client.models.export_to_df(
    space_id=SPACE_ID,
    model_name=MODEL_NAME,
    environment=Environments.TRAINING,
    model_version=MODEL_VERSION,
    start_time=start_time,
    end_time=end_time,
)
```

## Generate embeddings for your data

```python
import pandas as pd
from arize.embeddings import EmbeddingGenerator, UseCases

# You can check available models
print(EmbeddingGenerator.list_pretrained_models())

# Example dataframe
df = pd.DataFrame(
    {
        "text": [
            "Hello world.",
            "Artificial Intelligence is the future.",
            "Spain won the FIFA World Cup on 2010.",
        ],
    }
)
# Instantiate the generator for your usecase, selecting the base model
generator = EmbeddingGenerator.from_use_case(
    use_case=UseCases.NLP.SEQUENCE_CLASSIFICATION,
    model_name="distilbert-base-uncased",
    tokenizer_max_length=512,
    batch_size=100,
)

# Generate embeddings
df["text_vector"] = generator.generate_embeddings(text_col=df["text"])
```

## Operations on Datasets

### List Datasets

You can list all datasets that the user has access to using `client.datasets.list()`. You can use the `limit` parameter to specify the maximum number of datasets desired in the response and you can specify the `space_id` to target the list operation to a particular space.

```python
resp = client.datasets.list(
    limit=... # Optional
    space_id=... # Optional
)
```

The response is an object of type `DatasetsList200Response`, and you can access the list of datasets via its `datasets` attribute. In addition, you can transform the response object to a dictionary, to JSON format, or a pandas dataframe.

```python
# Get the list of datasets from the response
dataset_list = resp.datasets 
# Get the response as a dictionary
resp_dict = resp.to_dict()
# Get the response in JSON format
resp_dict = resp.to_json()
# Get the response as a pandas dataframe
resp_dict = resp.to_df()
```

### Create a Dataset

You can create a dataset using `client.datasets.create()`. You must pass examples, we currently don't support creating an empty dataset, for instance, these are 2 rows of examples, as a list of dictionaries. You can also pass a pandas dataframe for the examples.

```python
examples = [
    {
        "eval.Correctness Basic.explanation": "The query indicates that the user is having trouble accessing their account on their laptop, while access on their phone is still working. This suggests a potential issue with the login process on the laptop, which aligns with the 'Login Issues' queue. The mention of a possible change in the account could relate to login credentials or settings affecting the laptop specifically, but it still falls under the broader category of login issues.",
        "eval.Correctness Basic.label": "correct",
        "eval.Correctness Basic.score": 1,
        "llm output": "Login Issues",
        "query": "I can't get in on my laptop anymore, but my phone still works fine — could this be because I changed something in my account?"
    },
    {
        "eval.Correctness Basic.explanation": "The query is about a user who signed up but is unable to log in because the system says no account is found. This issue is related to the login process, as the user is trying to access their account and is facing a problem with the login system recognizing their account. Therefore, assigning this query to the 'Login Issues' queue is appropriate.",
        "eval.Correctness Basic.label": "correct",
        "eval.Correctness Basic.score": 1,
        "llm output": "Login Issues",
        "query": "Signed up ages ago but never got around to logging in — now it says no account found. Do I start over?"
    }
]
```

If the number of examples (rows in dataframe, items in list) is too large, the client SDK will try to send the data via Arrow Flight via gRPC for better performance. If you want to force the data transfer to HTTP you can use the `force_http` flag. The response is a `Dataset` object.

```python
created_dataset = client.datasets.create(
    space_i="<target-space-id>",
    name="<your-dataset-name>", # Name must be unique within a space
    examples=..., # List of dictionaries or pandas dataframe
)
```

The `Dataset` object also counts with convenience method similar to `List***` objects:

```python
# Get the response as a dictionary
dataset_dict = create_dataset.to_dict()
# Get the response in JSON format
dataset_dict = create_dataset.to_json()
```


### Get Dataset by ID

To get a dataset by its ID use `client.datasets.get()`, you can optionally also pass the version ID of a particular version of interest of the dataset. The returned type is `Dataset`.

```python
dataset = client.datasets.get(
    dataset_id=... # The unique identifier of the dataset
    dataset_version_id=... # The unique identifier of the dataset version
)
```

### Delete a Dataset

To delete a dataset by its ID use `client.datasets.delete()`. The call returns `None` if successful deletion took place, error otherwise.

```python
client.datasets.delete(
    dataset_id=... # The unique identifier of the dataset
)
```

# Configure Logging

## In Code

You can use `configure_logging` to set up the logging behavior of the Arize package to your needs. 

```python
from arize.logging import configure_logging

configure_logging(
    level=..., # Defaults to logging.INFO
    structured=..., # if True, emit JSON logs. Defaults to False
) 
```

## Via Environment Variables

Configure the same options as the section above, via:

```python
import os

# You can disable logging altogether
os.environ["ARIZE_LOG_ENABLE"] = "true" 
# Set up the logging level
os.environ["ARIZE_LOG_LEVEL"] = "debug" 
# Whether or not you want structured JSON logs
os.environ["ARIZE_LOG_STRUCTURED"] = "false" 
```

The default behavior of Arize's logs is: enabled, `INFO` level, and not structured.

# Community

Join our community to connect with thousands of AI builders.

- 🌍 Join our [Slack community](https://arize-ai.slack.com/join/shared_invite/zt-11t1vbu4x-xkBIHmOREQnYnYDH1GDfCg?__hstc=259489365.a667dfafcfa0169c8aee4178d115dc81.1733501603539.1733501603539.1733501603539.1&__hssc=259489365.1.1733501603539&__hsfp=3822854628&submissionGuid=381a0676-8f38-437b-96f2-fc10875658df#/shared-invite/email).
- 📚 Read our [documentation](https://docs.arize.com/arize).
- 💡 Ask questions and provide feedback in the _#arize-support_ channel.
- 𝕏 Follow us on [𝕏](https://twitter.com/ArizeAI).
- 🧑‍🏫 Deep dive into everything [Agents](http://arize.com/ai-agents/) and [LLM Evaluations](https://arize.com/llm-evaluation) on Arize's Learning Hubs.

Copyright 2025 Arize AI, Inc. All Rights Reserved.
