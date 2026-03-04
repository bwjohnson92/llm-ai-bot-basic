import os
from google import genai
from google.genai import types
def write_file(working_directory, file_path, content):

    absolute_path = os.path.abspath(working_directory)

    target_file = os.path.normpath(os.path.join(absolute_path, file_path))

    valid_target_file = os.path.commonpath([absolute_path, target_file]) == absolute_path

    if not valid_target_file:
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    
    # If it's a directory instead of a file
    if os.path.isdir(target_file):
        return f'Error: Cannot write to "{file_path}" as it is a directory'    

    try:
        # Ensure the target directory exists
        target_dir = os.path.dirname(target_file)
        os.makedirs(target_dir, exist_ok=True)

        with open(target_file, 'w') as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f'Error: An error occurred while writing to the file "{file_path}": {str(e)}'

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a specified file relative to the working directory, creating the file if it does not exist and overwriting it if it does",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to write to, relative to the working directory",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file",
            ),
        },
    ),
)