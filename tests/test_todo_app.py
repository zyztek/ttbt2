from unittest import mock
import json # For json.JSONDecodeError if needed for specific error testing
import os # For os.path.exists

# import runpy # No longer using runpy
from io import StringIO # Added

# Assuming todo_app.py is in the root directory or PYTHONPATH is set
from todo_app import TodoApp, main_cli # Import main_cli

class TestTodoApp:

    @mock.patch('todo_app.os.path.exists')
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('todo_app.json.load')
    def test_init_loads_todos_if_file_exists(self, mock_json_load, mock_open, mock_exists):
        mock_exists.return_value = True
        mock_todos_data = [{'task': 'Existing task', 'done': False}]
        mock_json_load.return_value = mock_todos_data

        app = TodoApp('dummy_path.json')

        mock_exists.assert_called_once_with('dummy_path.json')
        mock_open.assert_called_once_with('dummy_path.json', 'r')
        mock_json_load.assert_called_once_with(mock_open())
        assert app.todos == mock_todos_data

    @mock.patch('todo_app.os.path.exists')
    def test_init_empty_if_file_not_exists(self, mock_exists):
        mock_exists.return_value = False
        # Patch open and json.load as they might be called if os.path.exists is bypassed by mistake
        with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open, \
             mock.patch('todo_app.json.load') as mock_json_load:
            app = TodoApp('dummy_path.json')
            mock_exists.assert_called_once_with('dummy_path.json')
            assert app.todos == []
            mock_open.assert_not_called() # Should not be called if file doesn't exist
            mock_json_load.assert_not_called()


    @mock.patch('todo_app.TodoApp.save_todos') # Mock save_todos to prevent actual file write
    @mock.patch('builtins.print')
    def test_add_todo(self, mock_print, mock_save_todos):
        # Forcing __init__ to not load anything for this test's purpose
        with mock.patch('todo_app.os.path.exists', return_value=False):
            app = TodoApp()
        # app.todos = [] # Ensure it's empty for this test regardless of __init__ load

        app.add_todo("New Task 1")
        assert len(app.todos) == 1
        assert app.todos[0]['task'] == "New Task 1"
        assert app.todos[0]['done'] is False # Pytest style is False
        mock_save_todos.assert_called_once()
        mock_print.assert_called_with("Added: New Task 1")

        app.add_todo("New Task 2")
        assert len(app.todos) == 2
        assert app.todos[1]['task'] == "New Task 2"
        # assert_called_with checks the last call. For multiple, use assert_has_calls or check call_count
        # mock_save_todos.assert_called_with() # This would re-check the last call
        assert mock_save_todos.call_count == 2
        mock_print.assert_called_with("Added: New Task 2") # Checks last print call

    @mock.patch('builtins.print')
    def test_list_todos_empty(self, mock_print):
        with mock.patch('todo_app.os.path.exists', return_value=False):
            app = TodoApp()
        # app.todos = [] # Ensure empty, which it should be if file doesn't exist
        app.list_todos()
        mock_print.assert_called_once_with("No to-do items found.")

    @mock.patch('builtins.print')
    def test_list_todos_with_items(self, mock_print):
        with mock.patch('todo_app.os.path.exists', return_value=False):
            app = TodoApp()
        app.todos = [
            {'task': 'Task A', 'done': False},
            {'task': 'Task B', 'done': True}
        ]
        app.list_todos()

        expected_calls = [
            mock.call("1. [ ] Task A"),
            mock.call("2. [x] Task B")
        ]
        # Check if all expected calls were made, in any order if that's okay,
        # or specifically assert_has_calls for ordered sequence.
        # For this, the order matters.
        mock_print.assert_has_calls(expected_calls, any_order=False)

        # Ensure it doesn't print "No to-do items found."
        no_items_found_printed = False
        for call_arg_list in mock_print.call_args_list:
            if call_arg_list[0][0] == "No to-do items found.":
                no_items_found_printed = True
                break
        assert not no_items_found_printed, "'No to-do items found.' was printed unexpectedly."

    # Placeholder for more tests (save_todos, complete_todo, delete_todo)

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('todo_app.json.dump')
    def test_save_todos(self, mock_json_dump, mock_open):
        # Ensure __init__ doesn't try to load a file for this test
        with mock.patch('todo_app.os.path.exists', return_value=False):
            app = TodoApp('dummy_save.json')

        app.todos = [{'task': 'Task to save', 'done': False}]
        app.save_todos()

        mock_open.assert_called_once_with('dummy_save.json', 'w')
        mock_json_dump.assert_called_once_with(app.todos, mock_open(), indent=2)

    @mock.patch('todo_app.TodoApp.save_todos')
    @mock.patch('builtins.print')
    def test_complete_todo_valid_index(self, mock_print, mock_save_todos):
        with mock.patch('todo_app.os.path.exists', return_value=False):
            app = TodoApp()
        app.todos = [{'task': 'Task 1', 'done': False}]

        app.complete_todo(0) # Mark first task (index 0) as done

        assert app.todos[0]['done'] is True
        mock_save_todos.assert_called_once()
        mock_print.assert_called_with("Marked as done: Task 1")

    @mock.patch('todo_app.TodoApp.save_todos')
    @mock.patch('builtins.print')
    def test_complete_todo_invalid_index(self, mock_print, mock_save_todos):
        with mock.patch('todo_app.os.path.exists', return_value=False):
             app = TodoApp()
        app.todos = [{'task': 'Task 1', 'done': False}]

        app.complete_todo(1) # Index out of bounds
        assert app.todos[0]['done'] is False # Should not change
        mock_save_todos.assert_not_called()
        mock_print.assert_called_with("Invalid index.")

        # Reset print mock for the next call assertion if using unittest.TestCase style
        # For pytest, if checking all calls, list would be better or specific call index.
        # Here, assert_called_with checks the *last* call.
        app.complete_todo(-1) # Index out of bounds
        assert app.todos[0]['done'] is False
        assert mock_save_todos.call_count == 0 # Still not called
        mock_print.assert_called_with("Invalid index.") # Called again with this message

    @mock.patch('todo_app.TodoApp.save_todos')
    @mock.patch('builtins.print')
    def test_delete_todo_valid_index(self, mock_print, mock_save_todos):
        with mock.patch('todo_app.os.path.exists', return_value=False):
            app = TodoApp()
        app.todos = [
            {'task': 'Task 1 to delete', 'done': False},
            {'task': 'Task 2 keep', 'done': False}
        ]

        app.delete_todo(0) # Delete first task

        assert len(app.todos) == 1
        assert app.todos[0]['task'] == 'Task 2 keep'
        mock_save_todos.assert_called_once()
        mock_print.assert_called_with("Deleted: Task 1 to delete")

    @mock.patch('todo_app.TodoApp.save_todos')
    @mock.patch('builtins.print')
    def test_delete_todo_invalid_index(self, mock_print, mock_save_todos):
        with mock.patch('todo_app.os.path.exists', return_value=False):
            app = TodoApp()
        app.todos = [{'task': 'Task 1', 'done': False}]

        original_todos = list(app.todos) # shallow copy for comparison
        app.delete_todo(1) # Index out of bounds

        assert app.todos == original_todos
        mock_save_todos.assert_not_called()
        mock_print.assert_called_with("Invalid index.")

# Pytest will discover TestTodoApp class. No need for if __name__ == '__main__': unittest.main()


# It's often cleaner to have a dedicated test class for CLI tests
class TestTodoAppCLI:

    @mock.patch('todo_app.TodoApp') # Mock the TodoApp class itself
    @mock.patch('builtins.input')
    @mock.patch('builtins.print')
    def test_cli_add_and_list_and_exit(self, mock_print, mock_input, mock_todo_app_class):
        mock_app_instance = mock.MagicMock()
        mock_todo_app_class.return_value = mock_app_instance

        # Simulate user inputs: 1 (add), task, 2 (list), 5 (exit)
        # This test as originally designed is a bit complex for a single test
        # due to multiple user interactions in a loop.
        # The provided example was simplified to test 'add'.
        # We'll stick to the simplified version from the prompt.

        # Test 'add'
        # Re-patch input for this specific scenario
        with mock.patch('builtins.input', side_effect=['1', 'CLI Task Add', '5']):
            # We need to ensure that when runpy imports todo_app, our mock_todo_app_class is used.
            # This requires the mock to be active *before* runpy.run_module.
            # The class-level mock_todo_app_class should handle this if it's patching 'todo_app.TodoApp'

            # This requires the mock to be active *before* runpy.run_module.
            # The class-level mock_todo_app_class should handle this if it's patching 'todo_app.TodoApp'

            # Call main_cli directly
            try:
                main_cli()
            except StopIteration: # mock_input.side_effect will run out
                pass
            # SystemExit should not occur if '5' just breaks the loop

            mock_app_instance.add_todo.assert_called_with("CLI Task Add")

    @mock.patch('todo_app.TodoApp')
    @mock.patch('builtins.input', side_effect=['2', '5']) # List then Exit
    @mock.patch('builtins.print')
    def test_cli_list(self, mock_print, mock_input, mock_todo_app_class):
        mock_app_instance = mock.MagicMock()
        mock_todo_app_class.return_value = mock_app_instance
        try:
            main_cli()
        except StopIteration: pass
        mock_app_instance.list_todos.assert_called_once()

    @mock.patch('todo_app.TodoApp')
    @mock.patch('builtins.input', side_effect=['3', '1', '5']) # Complete, task 1, then Exit
    @mock.patch('builtins.print')
    def test_cli_complete(self, mock_print, mock_input, mock_todo_app_class):
        mock_app_instance = mock.MagicMock()
        mock_todo_app_class.return_value = mock_app_instance
        try:
            main_cli()
        except StopIteration: pass
        mock_app_instance.list_todos.assert_any_call() # Called before asking for index
        mock_app_instance.complete_todo.assert_called_once_with(0) # index is 1-based input - 1

    @mock.patch('todo_app.TodoApp')
    @mock.patch('builtins.input', side_effect=['4', '1', '5']) # Delete, task 1, then Exit
    @mock.patch('builtins.print')
    def test_cli_delete(self, mock_print, mock_input, mock_todo_app_class):
        mock_app_instance = mock.MagicMock()
        mock_todo_app_class.return_value = mock_app_instance
        try:
            main_cli()
        except StopIteration: pass
        mock_app_instance.list_todos.assert_any_call() # Called before asking for index
        mock_app_instance.delete_todo.assert_called_once_with(0)

    @mock.patch('todo_app.TodoApp') # Mock the class to prevent its __init__ from running
    @mock.patch('builtins.input', side_effect=['6', '5']) # Invalid choice, then Exit
    @mock.patch('builtins.print')
    def test_cli_invalid_choice(self, mock_print, mock_input, mock_todo_app_class):
        mock_app_instance = mock.MagicMock()
        mock_todo_app_class.return_value = mock_app_instance # Ensure TodoApp() returns our mock
        try:
            main_cli()
        except StopIteration: pass # Expected as input runs out
        # SystemExit should not occur with 'break'

        # Check if "Invalid choice." was printed.
        invalid_choice_printed = False
        if mock_print.call_args_list: # Ensure print was called at all
            for call_arg_list in mock_print.call_args_list:
                if "Invalid choice." in call_arg_list[0][0]:
                    invalid_choice_printed = True
                    break
        assert invalid_choice_printed, "Expected 'Invalid choice.' message not printed."
