"""
Módulo de aplicación de lista de tareas (To-Do) simple.

Proporciona una clase `TodoApp` para gestionar una lista de tareas,
con funcionalidades para añadir, listar, completar y eliminar tareas.
Las tareas se persisten en un archivo JSON.
También incluye una función `main_cli` para una interfaz de línea de comandos básica.
"""
import json
import os

class TodoApp:
    """
    Gestiona una lista de tareas (to-do items).

    Permite cargar tareas desde un archivo JSON, guardar tareas en el archivo,
    añadir nuevas tareas, listar todas las tareas, marcar tareas como completadas
    y eliminar tareas.
    """
    def __init__(self, storage_path='todo_storage.json'):
        """
        Inicializa la aplicación To-Do.

        Args:
            storage_path (str, optional): La ruta al archivo JSON donde se almacenan
                                          las tareas. Por defecto es 'todo_storage.json'.
        """
        self.storage_path = storage_path
        self.todos = self.load_todos()

    def load_todos(self):
        """
        Carga la lista de tareas desde el archivo de almacenamiento JSON.

        Si el archivo especificado en `self.storage_path` existe, intenta
        cargarlo y parsearlo como JSON.
        Si el archivo no existe o hay un error al parsear (ej. JSON malformado
        o archivo vacío que no es JSON válido), retorna una lista vacía.

        Returns:
            list: La lista de tareas cargada, o una lista vacía si no se pudo cargar.
        """
        if os.path.exists(self.storage_path):
            try: # Added try-except for robustness on load
                with open(self.storage_path, 'r', encoding='utf-8') as f: # Added encoding
                    # Handle empty file case for json.load
                    content = f.read()
                    if not content:
                        return []
                    return json.loads(content) # Changed from json.load(f) to handle empty string
            except (json.JSONDecodeError, IOError): # Added IOError
                return [] # Return empty list on error
        return []

    def save_todos(self):
        """
        Guarda la lista actual de tareas en el archivo de almacenamiento JSON.

        Sobrescribe el archivo especificado en `self.storage_path` con la lista
        actual de tareas, formateada como JSON con una indentación de 2 espacios.
        """
        with open(self.storage_path, 'w', encoding='utf-8') as f: # Added encoding
            json.dump(self.todos, f, indent=2)

    def add_todo(self, task):
        """
        Añade una nueva tarea a la lista.

        La nueva tarea se añade con el estado 'no completada' (`done: False`).
        Después de añadirla, se guardan todas las tareas y se imprime un mensaje.

        Args:
            task (str): La descripción de la tarea a añadir.
        """
        todo = {'task': task, 'done': False}
        self.todos.append(todo)
        self.save_todos()
        print(f"Added: {task}")

    def list_todos(self):
        """
        Imprime la lista de tareas actual en la consola.

        Si no hay tareas, imprime "No to-do items found.".
        De lo contrario, cada tarea se imprime con su número (basado en 1),
        su estado (`[x]` para completada, `[ ]` para no completada), y
        la descripción de la tarea.
        """
        if not self.todos:
            print("No to-do items found.")
            return
        for idx, todo in enumerate(self.todos, 1):
            status = '[x]' if todo['done'] else '[ ]'
            print(f"{idx}. {status} {todo['task']}")

    def complete_todo(self, index):
        """
        Marca una tarea como completada según su índice en la lista.

        El índice es 0-based (es decir, el primer elemento es el índice 0).
        Si el índice es válido, cambia el estado 'done' de la tarea a True,
        guarda la lista y imprime un mensaje de confirmación.
        Si el índice no es válido (fuera de rango), imprime "Invalid index.".

        Args:
            index (int): El índice (0-based) de la tarea a marcar como completada.
        """
        if 0 <= index < len(self.todos):
            self.todos[index]['done'] = True
            self.save_todos()
            print(f"Marked as done: {self.todos[index]['task']}")
        else:
            print("Invalid index.")

    def delete_todo(self, index):
        """
        Elimina una tarea de la lista según su índice.

        El índice es 0-based. Si el índice es válido, elimina la tarea
        de la lista, guarda los cambios e imprime un mensaje confirmando
        la eliminación con la descripción de la tarea eliminada.
        Si el índice no es válido, imprime "Invalid index.".

        Args:
            index (int): El índice (0-based) de la tarea a eliminar.
        """
        if 0 <= index < len(self.todos):
            removed = self.todos.pop(index)
            self.save_todos()
            print(f"Deleted: {removed['task']}")
        else:
            print("Invalid index.")

def main_cli():
    """
    Ejecuta el bucle principal de la interfaz de línea de comandos (CLI) para la aplicación To-Do.

    Presenta un menú al usuario para añadir, listar, completar o eliminar tareas,
    o para salir de la aplicación. Maneja la entrada del usuario y llama a los
    métodos correspondientes de la instancia `TodoApp`.
    """
    app = TodoApp()
    while True:
        print("\nTo-Do List Application")
        print("1. Add To-Do")
        print("2. List To-Dos")
        print("3. Mark To-Do as Done")
        print("4. Delete To-Do")
        print("5. Exit")
        choice = input("Choose an option: ")
        if choice == '1':
            task = input("Enter to-do task: ")
            app.add_todo(task)
        elif choice == '2':
            app.list_todos()
        elif choice == '3':
            try: # Added try-except for robust input parsing
                app.list_todos()
                idx_input = input("Enter task number to mark as done: ")
                if not idx_input.isdigit():
                    print("Invalid input. Please enter a number.")
                    continue
                idx = int(idx_input) - 1
                app.complete_todo(idx)
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif choice == '4':
            try: # Added try-except for robust input parsing
                app.list_todos()
                idx_input = input("Enter task number to delete: ")
                if not idx_input.isdigit():
                    print("Invalid input. Please enter a number.")
                    continue
                idx = int(idx_input) - 1
                app.delete_todo(idx)
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif choice == '5':
            print("Goodbye!")
            break # Use break to exit loop, sys.exit not strictly needed here
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main_cli()