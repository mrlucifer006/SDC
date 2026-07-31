import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "settings.json")

def get_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"malpractice_enabled": True}
    
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"malpractice_enabled": True}

def update_settings(new_settings):
    settings = get_settings()
    settings.update(new_settings)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)
