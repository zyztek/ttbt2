import json
import os

class ConfigLoader:
    @staticmethod
    def load(path):
        if path.endswith(".json"):
            with open(path, "r") as f:
                return json.load(f)
        # Add YAML or other loaders as needed
        return {}