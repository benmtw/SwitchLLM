import customtkinter as ctk
import json
import os
import requests
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Constants
BASE_DIR = Path(__file__).parent.resolve()
CONFIG_FILE = BASE_DIR / "config.json"
ENV_CHANGES_FILE = BASE_DIR / "env_changes.tmp"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/models"
DASHSCOPE_API_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/models"
NVIDIA_NIM_API_URL = "https://integrate.api.nvidia.com/v1/models"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class Config:
    def __init__(self):
        self._data = self._load()
    
    def _load(self) -> Dict[str, Any]:
        if not CONFIG_FILE.exists():
            return {"active_profile": "", "profiles": {}}
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {"active_profile": "", "profiles": {}}

    def save(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self._data, f, indent=2)

    @property
    def active_profile(self) -> str:
        return self._data.get("active_profile", "")

    @active_profile.setter
    def active_profile(self, value: str):
        self._data["active_profile"] = value

    @property
    def profiles(self) -> Dict[str, Any]:
        return self._data.get("profiles", {})

    @property
    def openrouter_key(self) -> str:
        return self._data.get("openrouter_api_key", "")

    @property
    def dashscope_key(self) -> str:
        return self._data.get("dashscope_api_key", "")

    @property
    def nvidia_key(self) -> str:
        return self._data.get("nvidia_api_key", "")

    def update_profile_model(self, profile_name: str, model: str):
        if profile_name in self.profiles:
            self.profiles[profile_name]["default_model"] = model
            self.save()

class SwitchLLMApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Switch Claude LLM Provider")
        self.geometry("500x450")
        self.config = Config()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Header
        self.header_label = ctk.CTkLabel(self, text="Select LLM Profile", font=("Roboto", 20, "bold"))
        self.header_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")

        # Profile Selection
        self.profile_var = ctk.StringVar(value=self.config.active_profile)
        self.profiles_frame = ctk.CTkScrollableFrame(self, label_text="Available Profiles")
        self.profiles_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        self.create_profile_radiobuttons()

        # Model Selection (Hidden by default, shared by openrouter/dashscope)
        self.model_frame = ctk.CTkFrame(self)
        self.model_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.model_frame.grid_remove()

        self.model_label = ctk.CTkLabel(self.model_frame, text="Model:")
        self.model_label.pack(side="left", padx=10)

        self.model_combobox = ctk.CTkComboBox(self.model_frame, width=300, command=self.on_model_change)
        self.model_combobox.pack(side="right", padx=10)
        self.model_combobox._entry.bind("<KeyRelease>", self.filter_models)

        # Apply Button
        self.apply_button = ctk.CTkButton(self, text="Apply & Exit", command=self.apply_and_exit, height=40)
        self.apply_button.grid(row=3, column=0, padx=20, pady=20, sticky="s")

        # Fetch model lists for dynamic profiles
        self.model_lists: Dict[str, list] = {}
        self.all_model_ids: list = []
        self._active_model_profile: Optional[str] = None

        if self.config.openrouter_key and "PLEASE_SET" not in self.config.openrouter_key:
            models = self.fetch_openrouter_models()
            self.model_lists["openrouter"] = [m["id"] for m in models]

        if self.config.dashscope_key and "PLEASE_SET" not in self.config.dashscope_key:
            models = self.fetch_dashscope_models()
            self.model_lists["dashscope"] = [m["id"] for m in models]

        if self.config.nvidia_key and "PLEASE_SET" not in self.config.nvidia_key:
            models = self.fetch_nvidia_models()
            self.model_lists["nvidia_nim"] = [m["id"] for m in models]

        # Show model dropdown if active profile needs it
        if self.config.active_profile in self.model_lists:
            self.show_model_dropdown(self.config.active_profile)

    def filter_models(self, event):
        if event.keysym in ["Up", "Down", "Return", "Tab", "Escape"]:
            return

        typed_text = self.model_combobox.get()
        if not typed_text:
            self.model_combobox.configure(values=self.all_model_ids)
            return

        filtered_models = [
            m for m in self.all_model_ids
            if typed_text.lower() in m.lower()
        ]
        self.model_combobox.configure(values=filtered_models)

    PROFILE_DISPLAY_NAMES = {
        "dashscope": "DASHSCOPE (Alibaba Cloud)",
        "nvidia_nim": "NVIDIA NIM",
    }

    def create_profile_radiobuttons(self):
        for profile_name in self.config.profiles.keys():
            display_name = self.PROFILE_DISPLAY_NAMES.get(profile_name, profile_name.upper())
            rb = ctk.CTkRadioButton(
                self.profiles_frame,
                text=display_name,
                variable=self.profile_var,
                value=profile_name,
                command=self.on_profile_select
            )
            rb.pack(anchor="w", pady=5, padx=10)

    def on_profile_select(self):
        selection = self.profile_var.get()
        if selection in self.model_lists:
            self.show_model_dropdown(selection)
        else:
            self.model_frame.grid_remove()

    def show_model_dropdown(self, profile_name: str):
        self._active_model_profile = profile_name
        self.all_model_ids = self.model_lists.get(profile_name, [])
        self.model_label.configure(text=f"{profile_name.upper()} Model:")
        self.model_combobox.configure(values=self.all_model_ids)
        current_model = self.config.profiles.get(profile_name, {}).get("default_model", "")
        if current_model in self.all_model_ids:
            self.model_combobox.set(current_model)
        else:
            self.model_combobox.set("")
        self.model_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

    def fetch_openrouter_models(self):
        print("Fetching models from OpenRouter...")
        try:
            response = requests.get(OPENROUTER_API_URL)
            if response.status_code == 200:
                data = response.json().get("data", [])
                models = [{"id": m["id"], "name": m["name"]} for m in data]
                models.sort(key=lambda x: x["id"])
                return models
        except Exception as e:
            print(f"Failed to fetch OpenRouter models: {e}")
        return []

    def fetch_dashscope_models(self):
        print("Fetching models from DashScope...")
        try:
            response = requests.get(
                DASHSCOPE_API_URL,
                headers={"Authorization": f"Bearer {self.config.dashscope_key}"}
            )
            if response.status_code == 200:
                data = response.json().get("data", [])
                models = [{"id": m["id"]} for m in data]
                models.sort(key=lambda x: x["id"])
                return models
        except Exception as e:
            print(f"Failed to fetch DashScope models: {e}")
        return []

    def fetch_nvidia_models(self):
        print("Fetching models from NVIDIA NIM...")
        try:
            response = requests.get(
                NVIDIA_NIM_API_URL,
                headers={"Authorization": f"Bearer {self.config.nvidia_key}"}
            )
            if response.status_code == 200:
                data = response.json().get("data", [])
                models = [{"id": m["id"]} for m in data]
                models.sort(key=lambda x: x["id"])
                return models
        except Exception as e:
            print(f"Failed to fetch NVIDIA NIM models: {e}")
        return []

    def on_model_change(self, choice):
        if self._active_model_profile:
            self.config.update_profile_model(self._active_model_profile, choice)

    def apply_and_exit(self):
        profile_name = self.profile_var.get()
        self.config.active_profile = profile_name
        self.config.save()
        
        profile_data = self.config.profiles.get(profile_name, {})
        
        # Initialize with all known variables as empty strings to ensure they are cleared 
        # if not explicitly set by the new profile.
        env_vars = {
            "ANTHROPIC_BASE_URL": "",
            "ANTHROPIC_AUTH_TOKEN": "",
            "ANTHROPIC_API_KEY": "",
            "ANTHROPIC_DEFAULT_SONNET_MODEL": "",
            "ANTHROPIC_DEFAULT_OPUS_MODEL": "",
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": ""
        }

        profile_type = profile_data.get("type", "")

        if profile_type == "openrouter":
            env_vars["ANTHROPIC_BASE_URL"] = "https://openrouter.ai/api"
            env_vars["ANTHROPIC_AUTH_TOKEN"] = self.config.openrouter_key
            env_vars["ANTHROPIC_API_KEY"] = ""  # Required by OpenRouter: explicitly blank to prevent conflicts
            selected_model = profile_data.get("default_model")
            if selected_model:
                env_vars["ANTHROPIC_DEFAULT_SONNET_MODEL"] = selected_model
                env_vars["ANTHROPIC_DEFAULT_OPUS_MODEL"] = selected_model
                env_vars["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = selected_model
        elif profile_type == "dashscope":
            env_vars["ANTHROPIC_BASE_URL"] = "https://dashscope-intl.aliyuncs.com/compatible-mode"
            env_vars["ANTHROPIC_API_KEY"] = self.config.dashscope_key
            selected_model = profile_data.get("default_model")
            if selected_model:
                env_vars["ANTHROPIC_DEFAULT_SONNET_MODEL"] = selected_model
                env_vars["ANTHROPIC_DEFAULT_OPUS_MODEL"] = selected_model
                env_vars["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = selected_model
        elif profile_type == "nvidia_nim":
            env_vars["ANTHROPIC_BASE_URL"] = "https://integrate.api.nvidia.com"
            env_vars["ANTHROPIC_AUTH_TOKEN"] = self.config.nvidia_key
        else:
            # Standard Logic (copy keys as is)
            for k, v in profile_data.items():
                if k.startswith("ANTHROPIC"):
                    env_vars[k] = v if v is not None else ""

        # Write to temp file
        with open(ENV_CHANGES_FILE, "w") as f:
            json.dump(env_vars, f)

        self.destroy()

if __name__ == "__main__":
    app = SwitchLLMApp()
    app.mainloop()
