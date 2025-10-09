# Fiddler Evals SDK

The Fiddler Evals SDK is a comprehensive toolkit for evaluating Large Language Model (LLM) applications. It provides a structured framework for creating, managing, and running evaluation datasets, experiments, and metrics to assess the performance and reliability of GenAI applications.

## Features

- **Dataset Management**: Create and manage evaluation datasets with structured test cases
- **Multiple Data Sources**: Import test cases from CSV, JSONL, and pandas DataFrames
- **Built-in Evaluators**: Comprehensive set of evaluation metrics including answer relevance, coherence, sentiment analysis, and more
- **Experiment Management**: Run and track evaluation experiments with detailed results
- **Integration**: Seamless integration with the Fiddler Platform for comprehensive AI monitoring

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Access to a Fiddler platform instance

### Installation

Install the Fiddler Evals SDK from PyPI:

```bash
pip install fiddler-evals
```

For the latest pre-release version:

```bash
pip install --upgrade --pre fiddler-evals
```

## Development Setup

### 1. Set Up Python

1. Install `uv` with `brew install uv`
2. Install Python with `uv python install`. This sets up a pre-built Python interpreter that respects `.python-version`

### 2. Install Dependencies

1. Install dependencies with `uv sync --locked`
2. Activate the virtual environment with `source .venv/bin/activate`

> **Note**: The first step creates a virtual environment at `.venv` if it doesn't exist yet. The file `uv.lock` defines our Python dependency tree including all transitive dependencies.

Read the [documentation for uv's project lockfile](https://docs.astral.sh/uv/concepts/projects/#project-lockfile) to familiarize yourself with the concept.

## Development

### Running Tests

```bash
make test
```

### Running Linter

```bash
make lint
```

## Usage Examples
Find the example notebooks in `examples/` directory.
