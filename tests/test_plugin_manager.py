from core.plugin_manager import PluginManager

def test_plugin_manager_load_and_execute(tmp_path):
    plugin_code = "def after_login(bot): bot.test_value = 42"
    plugin_path = tmp_path / "test_plugin.py"
    plugin_path.write_text(plugin_code)
    pm = PluginManager()
    pm.load_plugin(str(plugin_path))

    class DummyBot:
        pass

    bot = DummyBot()
    pm.execute_hook("after_login", bot=bot)
    assert bot.test_value == 42