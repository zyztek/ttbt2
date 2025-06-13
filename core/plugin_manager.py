import importlib.util
import sys
import os

class PluginManager:
    def __init__(self):
        self.hooks = {}

    def load_plugin(self, plugin_path):
        if not os.path.isfile(plugin_path):
            return
        spec = importlib.util.spec_from_file_location("plugin", plugin_path)
        plugin = importlib.util.module_from_spec(spec)
        sys.modules["plugin"] = plugin
        spec.loader.exec_module(plugin)
        for attr in dir(plugin):
            if not attr.startswith("_"):
                self.hooks[attr] = getattr(plugin, attr)

    def execute_hook(self, hook_name, *args, **kwargs):
        if hook_name in self.hooks:
            return self.hooks[hook_name](*args, **kwargs)
