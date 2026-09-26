# AI Agent Experiments

A collection of practical experiments with AI agents, automation, Python, research workflows, and real-world AI applications.

## About

This repository explores small, understandable tools for turning source text into useful structured content. Every experiment works from the command line, includes original sample data, and provides a deterministic local fallback. Optional OpenAI support is isolated so the provider can be replaced without rewriting the core workflows.

## Experiments

### 01. News Summarizer Agent

Turns news text into a conservative headline, concise summary, key points, and important entities.

### 02. Research Agent

Organizes supplied source material into a research topic, summary, findings, facts, entities, and questions for further research.

### 03. Telegram Content Agent

Converts longer news text into a concise Telegram-ready draft with a headline, short summary, and key information. It prepares text only and does not publish messages.

## Features

- Modular experiments with a shared utility layer
- Simple command-line tools
- Structured, source-grounded outputs
- UTF-8 source inputs capped at 100,000 bytes
- Deterministic local fallback with no API key required
- Optional reusable OpenAI provider integration with structural and grounding checks
- Beginner-friendly Python and automated CLI tests

## Tech Stack

- Python 3.10+
- OpenAI Python SDK (optional live LLM mode)
- Environment variables for configuration
- Git and GitHub

## Repository Structure

```text
ai-agent-experiments/
├── 01-news-summarizer-agent/
│   ├── app.py
│   ├── README.md
│   ├── sample_input.txt
│   └── sample_output.txt
├── 02-research-agent/
│   ├── app.py
│   ├── README.md
│   ├── sample_input.txt
│   └── sample_output.txt
├── 03-telegram-content-agent/
│   ├── app.py
│   ├── README.md
│   ├── sample_input.txt
│   └── sample_output.txt
├── tests/
│   ├── test_agent_utils.py
│   ├── test_news_summarizer.py
│   ├── test_research_agent.py
│   └── test_telegram_content.py
├── agent_utils.py
├── openai_provider.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/sa-noman/ai-agent-experiments
cd ai-agent-experiments
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, use `.venv\Scripts\Activate.ps1`.

### 3. Install the optional provider dependency

```bash
python -m pip install -r requirements.txt
```

Local fallback mode uses only the Python standard library. The dependency is needed only for `--use-llm`.

### 4. Configure optional live LLM access

```bash
cp .env.example .env
```

Edit `.env` locally and set `OPENAI_API_KEY`. Export those variables in your shell before running a live request; the programs do not automatically load `.env`.

### 5. Run an experiment

```bash
python 01-news-summarizer-agent/app.py 01-news-summarizer-agent/sample_input.txt
python 02-research-agent/app.py 02-research-agent/sample_input.txt
python 03-telegram-content-agent/app.py 03-telegram-content-agent/sample_input.txt
```

Add `--use-llm` to explicitly request live OpenAI output. If the provider is unavailable, the program reports a warning and safely uses the local fallback.

### 6. Run the tests

```bash
python -m unittest discover -s tests -v
```

## Future Experiments

Ideas for future work—not yet implemented:

- Web Research Agent
- Website Monitoring Agent
- AI Task Planner
- OSINT Note Organizer
- API Tool Agent

## Security

Secrets are not committed. `.env` and environment-specific variants are ignored, while `.env.example` documents the expected variable names. API credentials must be supplied through the local environment and are never hardcoded.

## Disclaimer

These projects are for learning and experimentation. Local extraction is heuristic, and live model responses may contain errors. Verify outputs and source claims before using them for important decisions or publication.
