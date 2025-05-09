# LANGGRAPH WORKSHOP

This repository contains the code for the LangGraph workshop we did on our R&D sessions.
The code is not meant to be nothing but pyhon spikes to test the LangGraph library.

## Installation

Create a virtual environment and install the requirements:

```bash
uv venv
source venv/bin/activate
uv pip install -r requirements.txt
```

Install the LangGraph CLI:

```bash
uv pip install -U "langgraph-cli[inmem]"
```

## Usage

Use the scripts simply by running them:

```bash
uv run memory.py
```

Launch the LangGraph studio to visualize graphs:

```bash
langraph dev
```

## Pitfalls

- To visualize the scripts in the LangGraph studio, you need to add them to `langgraph.json` file.
- LangGraph studio has its own memory, so for the script you need to view in the studio, dont declare the memory checkpoint in the script.
