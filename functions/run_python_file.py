import os
import subprocess
from google import genai
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file to execute",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Arguments to pass to the Python file",
            ),
        },
        required=["file_path"],
    ),
)

def run_python_file(working_directory, file_path, args=None):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))

        # Will be True or False
        valid_target_file = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs

        if not valid_target_file:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'

        if not target_file.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file'
        
        command = ["python", target_file]

        if args is not None:
            command.extend(args)  

        process = subprocess.run(command, cwd=working_dir_abs, text=True, capture_output=True, timeout=30)

        output_string = ""
        if process.returncode != 0:
            output_string += f"Process exited with code {process.returncode}\n"

        if process.stdout:
            output_string += f"STDOUT: {process.stdout}\n"

        if process.stderr:
            output_string += f"STDERR: {process.stderr}"

        if not process.stdout and not process.stderr:
            output_string += "No output produced"
            
        return output_string
    except Exception as e:
        return f"Error: executing Python file: {e}"
