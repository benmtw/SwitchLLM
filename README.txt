Switch Claude LLM Provider Tool
================================

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

Configuration Examples by Provider:

OpenRouter (Dynamic model selection):
{
  "openrouter_api_key": "sk-or-v1-your-key-here"
}

DashScope / Qwen (Dynamic model selection):
{
  "dashscope_api_key": "sk-your-dashscope-key"
}

NVIDIA NIM (Dynamic model selection):
{
  "nvidia_api_key": "nvapi-your-key-here"
}

Standard Profiles (add under "profiles" in config.json):

Kimi (Moonshot AI):
{
  "profiles": {
    "kimi": {
      "ANTHROPIC_BASE_URL": "https://api.moonshot.cn/anthropic",
      "ANTHROPIC_AUTH_TOKEN": "sk-your-kimi-key"
    }
  }
}

GLM (Zhipu AI):
{
  "profiles": {
    "glm": {
      "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
      "ANTHROPIC_AUTH_TOKEN": "your-glm-key"
    }
  }
}

DeepSeek:
{
  "profiles": {
    "deepseek": {
      "ANTHROPIC_BASE_URL": "https://api.deepseek.com",
      "ANTHROPIC_API_KEY": "sk-your-deepseek-key"
    }
  }
}

Claude Code Max (Standard OAuth):
{
  "profiles": {
    "claude_code_max": {}
  }
}

How to Run
----------
To make the environment variables persist in your CURRENT PowerShell session, you must "dot source" the script.

Run this command in PowerShell:

    . .\switch.ps1

(Note the space between the first dot and the script path).

If you just run `.\switch.ps1` without the leading dot, the variables will only be set for the duration of the script and will disappear when it finishes.

IMPORTANT: First-Time OpenRouter Users
--------------------------------------
If you have previously logged into Claude Code using Anthropic's standard OAuth (your Claude Max plan), you MUST run the `/logout` command in Claude Code BEFORE switching to OpenRouter or any other API-based provider.

1. Start a Claude Code session: claude
2. Run: /logout
3. Exit Claude Code
4. Run this tool to switch providers

This clears cached OAuth credentials that would otherwise conflict with the API key authentication.

Verification
------------
To verify that the variables have been set correctly in your current session, run:

    Get-ChildItem Env:ANTHROPIC*

You can also verify inside Claude Code by running:
    /status

Easy Access (Optional)
----------------------
Typing `. .\switch.ps1` every time can be tedious. You can set up a simple command (alias) like `switch-llm` to run it automatically.

NOTE: "Windows PowerShell" and "PowerShell" (v7) use different profile files. Follow these steps in whichever terminal you normally use. (If you use both, do this in both).

1. Open your PowerShell profile:
   notepad $PROFILE

2. Add this function to the end of the file:

   function switch-llm {
       . "C:\path\to\SwitchLLM\switch.ps1"
   }

3. Save and close notepad. Restart PowerShell.

Now you can just type `switch-llm` to launch the tool!

Features
--------
- **Kimi**: Pre-configured for Kimi (Moonshot AI) API.
- **GLM**: Pre-configured for Zhipu AI (GLM models).
- **OpenRouter**: Fetches available models dynamically from OpenRouter and allows you to select one from a dropdown list. Provides provider failover and usage analytics.
- **DashScope (Qwen)**: Fetches available models dynamically from Alibaba Cloud's DashScope API (Singapore endpoint) and allows you to select one from a dropdown list. Supports Qwen-Max, Qwen-Plus, Qwen-Turbo, QwQ, and other models.
- **NVIDIA NIM**: Fetches available models dynamically from NVIDIA's NIM API. Supports 150+ free models including Llama, Mistral, DeepSeek, Gemma, Phi, and more. NOTE: Requires a proxy/translator for full compatibility.
- **Claude Code Max**: A special profile that unsets all override environment variables. Use this if you want Claude Code to use your standard Max plan (via standard OAuth login) instead of an API key or custom endpoint.

Provider Documentation Links
-----------------------------
- OpenRouter: https://openrouter.ai/docs/guides/guides/claude-code-integration
- DashScope: https://help.aliyun.com/zh/model-studio/claude-code
- GLM/Zhipu: https://open.bigmodel.cn/dev/anthropic
- DeepSeek: https://api-docs.deepseek.com/zh-cn/guides/anthropic_api

Qwen pricing: https://www.alibabacloud.com/help/en/model-studio/model-pricing

Environment Variables Explanation
--------------------------------
By default, Claude Code handles everything through its built-in OAuth login flow—no environment variables needed. The credentials are stored in its own config files.

However, this tool uses environment variables as "overrides" for non-standard setups:

1. **ANTHROPIC_AUTH_TOKEN**: Used by most providers (Kimi, GLM, OpenRouter) for API key authentication.
2. **ANTHROPIC_API_KEY**: Used by some providers (DashScope, DeepSeek) for API key authentication.
3. **ANTHROPIC_BASE_URL**: Points Claude Code at a different endpoint.

**Important Authentication Rules**:
- Use EITHER ANTHROPIC_AUTH_TOKEN OR ANTHROPIC_API_KEY, never both simultaneously
- OpenRouter requires ANTHROPIC_API_KEY be explicitly set to empty string ("")
- Most providers use ANTHROPIC_AUTH_TOKEN with their API key

**Important**: If you previously set these variables to use another provider (like Kimi or GLM) and now want to go back to your standard Claude Max plan, select the **CLAUDE_CODE_MAX** profile in this tool. This will unset the overrides and allow Claude Code to resume its normal operation.
