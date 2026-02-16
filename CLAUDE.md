# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

SwitchLLM is a Windows utility that switches Claude Code between different LLM providers (Kimi, GLM, OpenRouter, or standard Claude Max) by setting `ANTHROPIC_*` environment variables in the current PowerShell session. It consists of a Python GUI (customtkinter) that writes env var selections to a temp file, and a PowerShell wrapper that applies those variables to the session.

## Running

```powershell
# Must be dot-sourced to persist env vars in the current session
. .\switch.ps1
```

The PowerShell script auto-detects `.venv\Scripts\python.exe` and falls back to system Python.

## Dependencies

```
pip install -r requirements.txt   # customtkinter, pydantic, requests, python-dotenv
```

## Architecture

Two-file system with a temp-file IPC mechanism:

1. **`switch_claude_llm_provider.py`** — CustomTkinter GUI app
   - `Config` class: loads/saves `config.json`, manages profiles and active selection
   - `SwitchLLMApp` class: GUI with radio buttons for profile selection, combobox for OpenRouter model picker with type-to-filter
   - On "Apply & Exit": writes env var dict to `env_changes.tmp` as JSON
   - OpenRouter models are fetched from the API and cached in `models_cache.json`

2. **`switch.ps1`** — PowerShell wrapper
   - Launches the Python GUI, reads `env_changes.tmp`, applies env vars via `[Environment]::SetEnvironmentVariable()` and `Set-Item`, then cleans up the temp file

## Key Files

- `config.json` — Profiles with API keys/URLs and active profile selection. **Contains secrets — never commit or expose.**
- `models_cache.json` — Cached OpenRouter model list (id + name)
- `env_changes.tmp` — Transient IPC file between Python and PowerShell (auto-deleted)

## Profile Types

- **Standard profiles** (kimi, glm, claude_code_max): env vars copied directly from config
- **OpenRouter profile**: special `"type": "openrouter"` — constructs env vars from `openrouter_api_key` and selected model, maps the model to all three model slots (opus/sonnet/haiku)
- **claude_code_max**: clears all override env vars so Claude Code uses its default OAuth flow
