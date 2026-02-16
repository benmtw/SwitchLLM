Switch Claude LLM Provider Tool
===============================

What is this?
-------------
This tool allows you to easily switch between different LLM providers (like Kimi, GLM, OpenRouter, and DashScope/Qwen) when using tools that expect the Anthropic API (like Claude Code). It works by injecting the correct environment variables (ANTHROPIC_BASE_URL, API keys, etc.) into your current shell session.

It provides a graphical user interface (GUI) to select your desired profile.

Setup
-----
1. Ensure you have Python installed.
2. Install the required Python dependencies:
   pip install -r requirements.txt

   (Note: The script attempts to use the local .venv if it exists).

Configuration
-------------
Edit `config.json` to add your API keys and customize profiles.
- For most providers, you need to set `ANTHROPIC_BASE_URL` and `ANTHROPIC_API_KEY`.
- For OpenRouter, simply add your `openrouter_api_key` to the top level of the config file.
- For DashScope (Alibaba Cloud / Qwen), add your `dashscope_api_key` to the top level of the config file.

How to Run
----------
To make the environment variables persist in your CURRENT PowerShell session, you must "dot source" the script.

Run this command in PowerShell:

    . .\switch.ps1

(Note the space between the first dot and the script path).

If you just run `.\switch.ps1` without the leading dot, the variables will only be set for the duration of the script and will disappear when it finishes.

Verification
------------
To verify that the variables have been set correctly in your current session, run:

    Get-ChildItem Env:ANTHROPIC*

Easy Access (Optional)
----------------------
Typing `. .\switch.ps1` every time can be tedious. You can set up a simple command (alias) like `switch-llm` to run it automatically.

NOTE: "Windows PowerShell" and "PowerShell" (v7) use different profile files. Follow these steps in whichever terminal you normally use. (If you use both, do this in both).

1. Open your PowerShell profile:
   notepad $PROFILE

2. Add this function to the end of the file:

   function switch-llm {
       . "d:\bentemp\SwitchLLM\switch.ps1"
   }

3. Save and close notepad. Restart PowerShell.

Now you can just type `switch-llm` to launch the tool!

Features
--------
- **Kimi**: Pre-configured for Kimi API.
- **GLM**: Pre-configured for Zhipu AI (GLM models).
- **OpenRouter**: Fetches available models dynamically from OpenRouter and allows you to select one from a dropdown list.
- **DashScope (Qwen)**: Fetches available models dynamically from Alibaba Cloud's DashScope API (Singapore endpoint) and allows you to select one from a dropdown list. Supports Qwen-Max, Qwen-Plus, Qwen-Turbo, QwQ, and other models available through the OpenAI-compatible API.
- **Claude Code Max**: A special profile that unsets all override environment variables. Use this if you want Claude Code to use your standard Max plan (via standard OAuth login) instead of an API key or custom endpoint.

Qweb pricing:https://www.alibabacloud.com/help/en/model-studio/model-pricing

Environment Variables Explanation
--------------------------------
By default, Claude Code handles everything through its built-in OAuth login flow—no environment variables needed. The credentials are stored in its own config files.

However, this tool uses two specific environment variables as "overrides" for non-standard setups:

1. **ANTHROPIC_AUTH_TOKEN**: Lets you override the default authentication with a raw API key. Useful if you want to use a personal API key (pay-as-you-go), a team/organization key, or authenticate through a CI/CD pipeline.
2. **ANTHROPIC_BASE_URL**: Lets you point Claude Code at a different endpoint. Useful for routing through a corporate proxy, using an Anthropic-compatible provider (e.g., AWS Bedrock, Google Vertex), or pointing to a local development/testing server.

**Important**: If you previously set these variables to use another provider (like Kimi or GLM) and now want to go back to your standard Claude Max plan, select the **CLAUDE_CODE_MAX** profile in this tool. This will unset the overrides and allow Claude Code to resume its normal operation.
