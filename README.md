# Ahoum Conversation Evaluation Benchmark

Production-ready benchmark for scoring every conversation turn across hundreds of facets spanning linguistic quality, pragmatics, safety, emotion, behavior, and domain-specific attributes. This project is designed to scale from 300 facets to 5000+ facets without changing the core architecture [file:2][file:256].

## Overview

The system evaluates each turn in a conversation independently, then aggregates turn-level outputs into conversation-level summaries. It uses an open-weights local model pipeline and stores structured JSON outputs with facet scores, confidence, evidence, and final aggregated scores [file:2][file:268][file:269].

## Project goals

- Score every conversation turn on a large facet set.
- Support confidence values for each score.
- Generate at least 50 evaluated conversations for submission.
- Remain architecture-stable as facet count grows from 300 to 5000+ [file:2].

## Expected structure

```text
project/
├── src/
│   ├── generate_conversations.py
│   ├── evaluator.py
│   ├── prompt_builder.py
│   └── preprocess.py
├── conversations/
│   ├── conv_*.json
│   └── ...
├── ui/
│   └── app.py
├── Facets-Assignment.csv
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Pipeline

### 1. Preprocess facets

The facet CSV is cleaned and normalized into a format suitable for prompting, batching, and downstream evaluation. Additional columns can be derived for category, polarity, scoring hints, and prompt grouping to improve scalability [file:2][file:256].

### 2. Build prompts dynamically

Prompt construction should be modular, facet-aware, and batchable. This avoids one-shot prompting and allows the system to scale by splitting large facet inventories into chunks while keeping output schemas consistent [file:2].

### 3. Evaluate turns

Each conversation turn is evaluated with the local model. For every applicable facet, the system stores:

- facet id
- facet name
- category
- score
- confidence
- evidence

This structure is already reflected in the generated conversation JSON files [file:268][file:269].

### 4. Aggregate outputs

Turn-level outputs are combined into conversation-level summaries with final conversation score and confidence, along with metadata such as total turns and source [file:269].

## Output format

Each generated conversation JSON should include:

```json
{
  "conversation_id": "conv_example_01",
  "turns": [...],
  "results": [...],
  "meta": {
    "total_turns": 2,
    "source": "ollama_api"
  }
}
```

Observed outputs in the attached files already follow this pattern, including per-turn facet scoring and metadata fields [file:268][file:269].

## Running locally

### Prerequisites

- Python 3.10+
- Ollama installed and running
- An open-weights model pulled locally, such as Qwen or Llama-family variants allowed by the assignment constraints [file:2]

### Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Pull model

```bash
ollama pull qwen2.5:1.5b
```

### Generate evaluated conversations

```bash
export MODEL_NAME=qwen2.5:1.5b
python src/generate_conversations.py
```

### Run UI

```bash
python ui/app.py
```

## Docker usage

### Build image

```bash
docker build -t ahoum-benchmark .
```

### Run container

```bash
docker run --rm -p 7860:7860   -e MODEL_NAME=qwen2.5:1.5b   -v $(pwd)/conversations:/app/conversations   ahoum-benchmark
```

### Compose

```bash
docker compose up --build
```

## Notes on scaling

To support 5000+ facets without redesign:

- Keep facets externalized in CSV or processed config.
- Batch facets by category or token budget.
- Use a stable JSON schema for all batches.
- Merge batch outputs deterministically.
- Preserve facet metadata separately from inference logic [file:2][file:256].

## Submission checklist

- GitHub repository with documentation.
- ZIP containing at least 50 conversations and their scores.
- Optional deployed UI.
- Open-weights model usage only [file:2].

## Known observations

The attached JSON outputs show that the current system is generating very large per-turn score payloads with confidence and evidence fields, which is aligned with the benchmark objective. However, if the script is not running, the most likely issues are model availability, Ollama connectivity, missing dependencies, or malformed local source files rather than the output format itself [file:268][file:269].
