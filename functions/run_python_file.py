import os
import subprocess
from google import genai
from google.genai import types
def run_python_file(working_directory, file_path, args=None):

    absolute_path = os.path.abspath(working_directory)

    target_file = os.path.normpath(os.path.join(absolute_path, file_path))

    valid_target_file = os.path.commonpath([absolute_path, target_file]) == absolute_path

    if not valid_target_file:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(target_file):
        return f'Error: "{file_path}" does not exist or is not a regular file'
    
    if not target_file.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file'

    try:
        command = ["python", target_file]
        if args:
            command.extend(args)
        
        result = subprocess.run(command, capture_output=True, text=True, cwd=absolute_path, timeout=30)
        
        output_string = ""
        if result.returncode != 0:
            output_string += f'Error: Process exited with code {result.returncode}\n'
        if not result.stdout and not result.stderr:
            output_string += f'No output produced'
        if result.stdout:
            output_string += f'STDOUT:{result.stdout}'
        if result.stderr:
            output_string += f'STDERR:{result.stderr}'
        
        return output_string
    except Exception as e:
        return f"Error: executing Python file: {e}"

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a specified Python file relative to the working directory, with optional arguments, and returns its output.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file to execute, relative to the working directory",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Optional list of string arguments to pass to the Python file when executing",
            ),
        },
    ),
)