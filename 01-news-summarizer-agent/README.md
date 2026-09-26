# News Summarizer Agent

## Overview

A small command-line experiment that turns a UTF-8 news text file into a headline, concise summary, key points, and important entities.

## Features

- Structured, source-grounded output
- Deterministic local extractive fallback
- Optional OpenAI integration
- Clear errors for missing, empty, or non-UTF-8 input

## How It Works

The local mode scores and selects sentences already present in the source, so it does not intentionally add facts. With `--use-llm`, provider logic in `openai_provider.py` requests a grounded structured response and falls back locally if the provider is unavailable.

## Installation

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env`, then set `OPENAI_API_KEY` only if live OpenAI output is wanted. Do not commit `.env`. `OPENAI_MODEL` is optional.

## Usage

```bash
python 01-news-summarizer-agent/app.py 01-news-summarizer-agent/sample_input.txt
python 01-news-summarizer-agent/app.py 01-news-summarizer-agent/sample_input.txt --use-llm
```

## Example

The first command reads `sample_input.txt`. Its verified local result is stored in `sample_output.txt` and labeled **Example Output** because no live model produced it.

## Limitations

The local fallback is extractive rather than generative. Its entity detection is heuristic, and it does not independently verify the source. Live model output can still be wrong and should be reviewed.
