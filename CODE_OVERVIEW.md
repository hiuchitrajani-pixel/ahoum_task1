# Code Overview: Ahoum AI Q1

This file explains the main components and workflow of the project in one place.

## Purpose

Ahoum AI Q1 is a conversation evaluation platform that:
- generates a set of scenario-based conversation turns,
- evaluates conversation turns on multiple facets using an LLM,
- provides a Streamlit interface for scoring and exploring results,
- stores conversation and evaluation output as JSON.

## Main Components

### 1. `src/generate_conversations.py`
- Builds a list of hard-coded conversation examples.
- Includes distress, hostility, empathy, technical questions, sarcasm, spiritual, ethical, decision-making, and other scenario turns.
- Calls `evaluate_conversation()` from `src/evaluator.py` for each conversation.
- Saves results into `conversations/conv_*.json` files.

### 2. `src/evaluator.py`
- Central evaluation engine.
- Loads scoring "facets" from `data/facets_cleaned.csv`.
- Sends batches of facets and a single conversation turn to an Ollama model via its API.
- Parses the model JSON output into facet scores and confidence values.
- Default scoring configuration is controlled by environment variables:
  - `OLLAMA_URL`
  - `MODEL_NAME`
  - `BATCH_SIZE`
  - `MAX_RETRIES`
  - `RETRY_DELAY`
- Supports:
  - `evaluate_turn(...)` for one turn,
  - `evaluate_conversation(...)` for a full multi-turn conversation.

### 3. `src/prompt_builder.py`
- Builds the chat prompt sent to the LLM.
- Defines the system prompt and few-shot example.
- Includes `make_batches()` to split facets into smaller groups.
- Prompts the model to return only a valid JSON array.

### 4. `src/preprocess.py`
- Converts raw facet data from `data/facets_raw.csv` into a clean CSV (`data/facets_cleaned.csv`).
- Cleans facet names, assigns IDs and categories.
- Marks whether each facet is observable from text.
- Adds metadata such as `scoring_direction`, `score_scale`, and `rubric_score_1/5`.

### 5. `ui/app.py`
- Streamlit app for interactive evaluation and browsing.
- UI tabs:
  - Single Turn evaluation
  - Full Conversation editor
  - Browse saved results
  - Facet Explorer
- Uses `src/evaluator.py` to score turns live.
- Loads saved conversation JSON files from `conversations/`.
- Reads cleaned facet metadata from `data/facets_cleaned.csv`.
- Includes fallback mock scoring if evaluation fails.

## Data Files

### `conversations/`
- Contains generated JSON results for evaluated conversations.
- Each file includes:
  - `conversation_id`
  - `turns`
  - `results` (facet scores)
  - `meta`

### `data/facets_raw.csv`
- Original facet definitions.
- Used by `src/preprocess.py`.

### `data/facets_cleaned.csv`
- Cleaned and normalized facet metadata.
- Used by `src/evaluator.py` and `ui/app.py`.

## Docker Setup

### `docker-compose.yml`
- Launches two services:
  - `ollama`: Ollama model server
  - `app`: application container with access to data and conversations
- Shares data directories into the app container.
- Exposes:
  - Ollama API on `11434`
  - Streamlit on `8501`

## Execution Flow

### Typical batch evaluation flow
1. `python src/generate_conversations.py`
2. It builds full conversation list in `build_all_conversations()`.
3. Calls `evaluate_conversation()` for each conversation.
4. `evaluate_conversation()` loops through turns and calls `evaluate_turn()`.
5. `evaluate_turn()` batches facets and sends requests to the model.
6. Responses are parsed and saved to `conversations/*.json`.

### Interactive UI flow
1. Run `streamlit run ui/app.py`.
2. In the app, choose a model and categories.
3. Enter text for a single turn or full conversation.
4. The app calls `evaluate_turn()` and displays facet scores.
5. Saved conversation files can be browsed in the UI.

## How to Run

### Local Python
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python src/preprocess.py
python src/generate_conversations.py
cd ui
streamlit run app.py
```

### Docker Compose
```bash
docker compose up --build
```

> Note: The project expects Ollama to be available at `http://localhost:11434/api/chat` by default.

## Key Files at a Glance

| File | Role |
|------|------|
| `src/generate_conversations.py` | Generates conversations and saves evaluation JSON files |
| `src/evaluator.py` | Sends turns to the LLM, parses facet scoring results |
| `src/prompt_builder.py` | Builds the LLM prompt and batches facets |
| `src/preprocess.py` | Cleans raw facet CSV into usable metadata |
| `ui/app.py` | Streamlit front-end for evaluation and exploration |
| `docker-compose.yml` | Defines services for Ollama and the app |
| `requirements.txt` | Python dependencies |

## Notes
- The model evaluation is done turn-by-turn, not conversation-level.
- The app currently uses a fallback path when the model call fails.
- `data/facets_cleaned.csv` is the primary metadata source for scoring facets.

If you want, I can also create a second short cheat-sheet that explains just the runtime flow in one paragraph.