# veris-cli

[![PyPI version](https://badge.fury.io/py/veris-cli.svg)](https://badge.fury.io/py/veris-cli)
[![Tests](https://github.com/veris-ai/veris-cli/actions/workflows/test.yml/badge.svg)](https://github.com/veris-ai/veris-cli/actions/workflows/test.yml)
[![Python](https://img.shields.io/pypi/pyversions/veris-cli.svg)](https://pypi.org/project/veris-cli/)

Veris CLI connects a local agent to the Veris simulation backend so you can generate scenarios and run end-to-end evaluations.

## Quickstart

### Before you start

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed

If you want to run simulationa against you local agent you need ngrok setup:
Follow: https://ngrok.com/docs/getting-started/

You need to have an API key and Agent ID from the Veris team.

### Installation

```
uv add tool veris-cli
```

### Initialize (one time only)

IMPORTANT: Get your VERIS_API_KEY and VERIS_AGENT_ID if you don't have it already. Ask us on Slack or email developers@veris.ai if need help.

```bash
veris init --veris-api-key YOUR_API_KEY --veris-agent-id YOUR_AGENT_ID
```

This creates `.veris/config.yaml` with your credentials.

## Commands

### Local Setup

If you're running a local agent, use ngrok to create a public tunnel:

```bash
# Start tunnel in background (default)
veris setup-local start --local-url http://localhost:8000

# Run in foreground (blocks until Ctrl+C)
veris setup-local start --local-url http://localhost:8000 --foreground

# Stop all tunnels
veris setup-local stop
```

This saves the public URL to `.veris/config.yaml` under `PUBLIC_AGENT_URL`.

### Agent Management

```bash
# Show agent information
veris agent show

# Or specify a different agent
veris agent show --agent-id AGENT_ID
```

### Scenario Management

```bash
# List scenario sets for your agent
veris scenario list

# Or specify a different agent
veris scenario list --agent-id AGENT_ID
```

### Simulation

```bash
# Launch simulation
veris simulation launch --scenario-set-id SET_ID --max-turns 20 --watch

# Launch with custom agent connection settings
veris simulation launch \
  --scenario-set-id SET_ID \
  --max-turns 20 \
  --agent-url https://your-agent.com \
  --agent-transport http \
  --agent-timeout 300 \
  --watch

# Get simulation status
veris simulation status --run-id RUN_ID

# Get sessions
veris simulation sessions --run-id RUN_ID

# Get logs (all sessions or specific session)
veris simulation logs --run-id RUN_ID
veris simulation logs --run-id RUN_ID --session-id SESSION_ID

# Get results
veris simulation results --run-id RUN_ID

# Kill running simulation
veris simulation kill --run-id RUN_ID
```

## Configuration

Credentials and settings are stored in `.veris/config.yaml`:

```yaml
VERIS_API_KEY: your_api_key
VERIS_AGENT_ID: your_agent_id
VERIS_API_URL: https://simulator.api.veris.ai/
PUBLIC_AGENT_URL: https://xxxx.ngrok.io  # Set by setup-local
```

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Format code
uv run ruff format

# Lint
uv run ruff check --fix
```
