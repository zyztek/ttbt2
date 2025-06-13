import json
import os
import yaml # Added import

class ConfigLoader:
    @staticmethod
    def load(path):
        if path.endswith(".json"):
            # Added encoding="utf-8"
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        # Added YAML loading capability
        elif path.endswith((".yml", ".yaml")):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except yaml.YAMLError:
                # Handle YAML parsing errors, perhaps log and return empty dict
                return {} # Or raise an exception
        # Fallback for unrecognized file types
        return {}