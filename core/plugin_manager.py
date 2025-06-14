"""
Módulo para la gestión de plugins dinámicos.

Este sistema permite cargar módulos de Python como plugins en tiempo de ejecución.
Los plugins pueden definir funciones (hooks) que la aplicación principal puede
descubrir y ejecutar en puntos específicos de su ciclo de vida, permitiendo
extender o modificar el comportamiento de la aplicación sin alterar su código base.
"""
import importlib.util
import sys
import os

class PluginManager:
    """
    Gestiona la carga y ejecución de hooks definidos en plugins externos.

    Los plugins son módulos de Python que pueden contener funciones (hooks).
    El PluginManager carga estos módulos, registra sus funciones públicas
    (aquellas que no comienzan con '_') como hooks, y permite su ejecución
    por nombre.
    """
    def __init__(self):
        """
        Inicializa el PluginManager.

        Crea un diccionario vacío para almacenar los hooks registrados
        de los plugins cargados.
        """
        self.hooks = {}

    def load_plugin(self, plugin_path):
        """
        Carga un plugin desde la ruta de archivo especificada.

        Si la ruta no es un archivo válido, el método retorna sin acción.
        De lo contrario, el módulo es cargado, y todas sus funciones públicas
        (que no empiezan con '_') son registradas como hooks disponibles.
        El nombre del hook será el nombre de la función.

        Args:
            plugin_path (str): La ruta completa al archivo .py del plugin.
        """
        if not os.path.isfile(plugin_path):
            # Considerar logging una advertencia aquí si el path no es válido.
            return

        # Usar un nombre de módulo único basado en el path para evitar colisiones
        # si se cargan múltiples plugins con funciones homónimas pero de distintos archivos.
        # Por simplicidad, el ejemplo original usa "plugin", pero esto podría ser problemático.
        # module_name = f"plugin_{os.path.basename(plugin_path).replace('.py', '')}"
        # Sin embargo, para mantener la lógica original de sys.modules["plugin"] = plugin
        # se usará "plugin" como nombre de módulo, aunque esto implica que solo un "plugin"
        # con este nombre de módulo puede estar realmente en sys.modules a la vez de esta forma.
        # Una mejor práctica sería usar nombres únicos o no manipular sys.modules directamente
        # si no es estrictamente necesario para el comportamiento del plugin.

        try:
            spec = importlib.util.spec_from_file_location("plugin", plugin_path)
            if spec is None or spec.loader is None:
                # Log error: no se pudo crear spec o no hay loader
                print(f"[PluginManager] Error: No se pudo crear spec para {plugin_path}")
                return

            plugin = importlib.util.module_from_spec(spec)

            sys.modules["plugin"] = plugin # Restored as per original logic

            spec.loader.exec_module(plugin)

            for attr_name in dir(plugin):
                if not attr_name.startswith("_"):
                    attribute = getattr(plugin, attr_name)
                    if callable(attribute): # Registrar solo funciones/callables como hooks
                        self.hooks[attr_name] = attribute
        except Exception as e:
            # Log error: Fallo al cargar el plugin
            print(f"[PluginManager] Error al cargar plugin {plugin_path}: {e}")


    def execute_hook(self, hook_name, *args, **kwargs):
        """
        Ejecuta un hook registrado por su nombre.

        Si el hook_name existe en el diccionario de hooks, se llama
        pasándole los argumentos y keyword arguments proporcionados.
        Si el hook no se encuentra, el método retorna None y no lanza error.

        Args:
            hook_name (str): El nombre del hook a ejecutar.
            *args: Argumentos posicionales a pasar al hook.
            **kwargs: Argumentos de palabra clave a pasar al hook.

        Returns:
            El resultado de la ejecución del hook, o None si el hook no existe.
        """
        if hook_name in self.hooks:
            return self.hooks[hook_name](*args, **kwargs)
        # Considerar logging una advertencia si el hook no se encuentra.
        return None
