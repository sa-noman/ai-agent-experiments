# Telegram Content Agent

## Overview

A simple CLI experiment that converts long news text into a concise, Telegram-ready post with a headline, short summary, and key information.

## Features

- Concise, factual structure
- No intentional clickbait or unsupported additions
- Deterministic local extractive fallback
- Optional OpenAI integration

## How It Works

Local mode selects a small number of high-signal source sentences and formats them for quick reading. With `--use-llm`, the isolated provider requests the same structure while instructing the model to stay within the source.

## Installation

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Set `OPENAI_API_KEY` in an uncommitted `.env` file only for live output. `OPENAI_MODEL` is optional. Local mode requires no key.

## Usage

```bash
python 03-telegram-content-agent/app.py 03-telegram-content-agent/sample_input.txt
python 03-telegram-content-agent/app.py 03-telegram-content-agent/sample_input.txt --use-llm
```

## Example

The first command reproduces `sample_output.txt`. The saved result is labeled **Example Output** because it came from the local fallback, not a live model.

## Limitations

The program does not publish to Telegram. It prepares text only. Local sentence selection may be less concise than human editing, and neither mode independently verifies source claims.
