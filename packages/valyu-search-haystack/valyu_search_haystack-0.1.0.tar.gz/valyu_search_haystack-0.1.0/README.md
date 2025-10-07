---
layout: integration
name: Valyu Search
description: Search and content extraction components using Valyu's API for web and proprietary sources
authors:
  - name: Valyu
    socials:
      github: valyu
pypi: https://pypi.org/project/valyu-search-haystack
repo: https://github.com/valyu/valyu-search-haystack
type: Search & Content Extraction
report_issue: https://github.com/valyu/valyu-search-haystack/issues
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [ValyuSearch](#valyusearch)
  - [ValyuContentFetcher](#valyucontentfetcher)
  - [RAG Pipeline Example](#rag-pipeline-example)
  - [Combined Search and Content Fetching](#combined-search-and-content-fetching)
  - [Advanced Configuration](#advanced-configuration)
- [Examples](#examples)
- [API Integration Details](#api-integration-details)
  - [Authentication](#authentication)
  - [Endpoints](#endpoints)
  - [Error Handling](#error-handling)
  - [License](#license)

## Overview

[![PyPI - Version](https://img.shields.io/pypi/v/valyu-search-haystack.svg)](https://pypi.org/project/valyu-search-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/valyu-search-haystack.svg)](https://pypi.org/project/valyu-search-haystack)

Haystack components for integrating Valyu's powerful search and content extraction APIs into your Haystack pipelines.

This package provides two main components:

- **`ValyuSearch`** - Search component that queries the Valyu DeepSearch API and returns documents with content already included
- **`ValyuContentFetcher`** - Content extraction component that fetches and cleans content from URLs

**Key Features:**

- Search across web and proprietary sources
- Full content included in search results
- AI-powered content extraction and summarization

---

## Installation

Use `pip` to install Valyu Search for Haystack:

```console
pip install valyu-search-haystack
```

Or install from source:

```console
pip install -e .
```

**Requirements:**

- Python 3.8+
- haystack-ai >= 2.0.0
- valyu >= 2.2.1

## Usage

Set your Valyu API key as an environment variable:

```bash
export VALYU_API_KEY="your-api-key"
```

### ValyuSearch

The `ValyuSearch` component integrates with the Valyu DeepSearch API. Unlike many search APIs, Valyu returns full content by default, making it ideal for RAG pipelines.

**Basic Usage:**

```python
from valyu_haystack import ValyuSearch
from haystack import Pipeline

# Create a search component (API key from VALYU_API_KEY env var)
search = ValyuSearch(
    top_k=5,
    search_type="all",  # "web", "proprietary", or "all"
    relevance_threshold=0.5
)

# Create and run a pipeline
pipeline = Pipeline()
pipeline.add_component("search", search)

result = pipeline.run({"search": {"query": "What is Haystack AI?"}})
documents = result["search"]["documents"]
links = result["search"]["links"]
```

**Component Parameters:**

- `api_key` (Secret): Your Valyu API key. Defaults to `VALYU_API_KEY` environment variable
- `top_k` (int, default=10): Maximum number of results to return
- `api_base_url` (str): Base URL for the Valyu API
- `search_type` (Literal["web", "proprietary", "all"], default="all"): Type of search
- `relevance_threshold` (float, default=0.5): Minimum relevance score (0.0-1.0)
- `max_price` (int, default=100): Maximum price per thousand queries in cents

**Output:**

- `documents` (List[Document]): Documents with content and rich metadata
- `links` (List[str]): List of URLs from search results

**Metadata included:**

- `title`: Page title
- `url`: Source URL
- `description`: Page description
- `source`: Data source identifier
- `relevance_score`: Relevance score (0.0-1.0)
- `price`: Cost of this result
- `length`: Content length in characters
- `data_type`: Type of data ("structured" or "unstructured")
- `image_url`: Associated image URL (if any)

### ValyuContentFetcher

The `ValyuContentFetcher` component extracts clean, readable content from URLs using the Valyu Contents API. It supports batch processing and AI-powered summarization.

**Basic Usage:**

```python
from valyu_haystack import ValyuContentFetcher
from haystack import Pipeline

# Create a content fetcher component
fetcher = ValyuContentFetcher(
    extract_effort="normal",  # "normal", "high", or "auto"
    response_length="short",  # "short", "medium", "large", "max", or int
    summary=True  # Enable AI summarization
)

# Create and run a pipeline
pipeline = Pipeline()
pipeline.add_component("fetcher", fetcher)

urls = ["https://example.com/article1", "https://example.com/article2"]
result = pipeline.run({"fetcher": {"urls": urls}})
documents = result["fetcher"]["documents"]
```

**Component Parameters:**

- `api_key` (Secret): Your Valyu API key. Defaults to `VALYU_API_KEY` environment variable
- `api_base_url` (str): Base URL for the Valyu API
- `timeout` (int, default=30): Request timeout in seconds
- `extract_effort` (Literal["normal", "high", "auto"], optional): Extraction thoroughness
- `response_length` (Union[Literal["short", "medium", "large", "max"], int], optional): Content length per URL
- `summary` (Union[bool, str, Dict], optional): AI summary config
  - `False` or `None`: No AI processing (raw content)
  - `True`: Basic automatic summarization
  - `str`: Custom instructions (max 500 chars)
  - `dict`: JSON schema for structured extraction

**Input:**

- `urls` (List[str], optional): List of URLs to fetch
- `documents` (List[Document], optional): Documents with URLs in metadata

**Output:**

- `documents` (List[Document]): Documents with extracted content

**Metadata included:**

- `url`: Source URL
- `title`: Page title
- `length`: Content length in characters
- `source`: Data source identifier
- `data_type`: Type of content

### RAG Pipeline Example

Combine `ValyuSearch` with other Haystack components to build a complete RAG pipeline:

```python
from valyu_haystack import ValyuSearch
from haystack import Pipeline
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder
from haystack.utils import Secret

# Create components
search = ValyuSearch(top_k=5)
prompt_builder = PromptBuilder(template="""
Answer the question based on the following context:

Context:
{% for doc in documents %}
{{ doc.content }}
{% endfor %}

Question: {{ query }}
Answer:
""")
generator = OpenAIGenerator(api_key=Secret.from_env_var("OPENAI_API_KEY"))

# Build pipeline
pipeline = Pipeline()
pipeline.add_component("search", search)
pipeline.add_component("prompt", prompt_builder)
pipeline.add_component("llm", generator)

# Connect components
pipeline.connect("search.documents", "prompt.documents")
pipeline.connect("prompt.prompt", "llm.prompt")

# Run RAG pipeline
result = pipeline.run({
    "search": {"query": "What is Haystack?"},
    "prompt": {"query": "What is Haystack?"}
})

answer = result["llm"]["replies"][0]
```

### Combined Search and Content Fetching

Since `ValyuSearch` already returns content, `ValyuContentFetcher` is typically used for additional URLs or re-fetching with different parameters:

```python
from valyu_haystack import ValyuSearch, ValyuContentFetcher
from haystack import Pipeline

# Create components
search = ValyuSearch(top_k=3)
fetcher = ValyuContentFetcher(
    extract_effort="high",  # More thorough extraction
    summary=True  # Add AI summaries
)

# Create pipeline
pipeline = Pipeline()
pipeline.add_component("search", search)
pipeline.add_component("fetcher", fetcher)

# Connect - fetcher will re-fetch content with enhanced extraction
pipeline.connect("search.documents", "fetcher.documents")

result = pipeline.run({"search": {"query": "machine learning"}})
enhanced_documents = result["fetcher"]["documents"]
```

### Advanced Configuration

**Using explicit API key:**

```python
from haystack.utils import Secret
from valyu_haystack import ValyuSearch

search = ValyuSearch(
    api_key=Secret.from_token("your-api-key"),
    top_k=10,
    search_type="proprietary",  # Search only proprietary sources
    relevance_threshold=0.7  # Higher relevance threshold
)
```

**Structured data extraction with Content Fetcher:**

```python
from valyu_haystack import ValyuContentFetcher

# Define JSON schema for structured extraction
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "author": {"type": "string"},
        "published_date": {"type": "string"},
        "summary": {"type": "string"}
    }
}

fetcher = ValyuContentFetcher(summary=schema)
result = fetcher.run(urls=["https://example.com/article"])

# Extracted structured data will be in document metadata
```

## Examples

Check out the `examples/` directory for more detailed examples:

- `basic_search.py` - Simple search example
- `search_with_content_fetcher.py` - Using both components together
- `rag_pipeline.py` - Building a RAG pipeline with mock LLM
- `standalone_content_fetcher.py` - Using content fetcher independently
- `real_api_example.py` - Additional search API example
- `real_content_api_example.py` - Additional content API example

Run examples:

```bash
export VALYU_API_KEY="your-api-key"
python examples/basic_search.py
```

## API Integration Details

### Authentication

Both components use Haystack's `Secret` class for secure API key management:

- Header: `x-api-key: your-api-key`
- Environment variable: `VALYU_API_KEY`

### Endpoints

- **Search:** `https://api.valyu.network/v1/deepsearch`
- **Contents:** `https://api.valyu.network/v1/contents`

### Error Handling

Components raise specific exceptions:

- `ValyuSearchError`: Errors from the search API
- `ValyuContentFetcherError`: Errors from the content API
- `TimeoutError`: Request timeouts

### License

`valyu-search-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
