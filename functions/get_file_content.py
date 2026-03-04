import os
from google import genai
from google.genai import types

def get_file_content(working_directory, file_path):
    absolute_path = os.path.abspath(working_directory)

    target_file = os.path.normpath(os.path.join(absolute_path, file_path))

    valid_target_file = os.path.commonpath([absolute_path, target_file]) == absolute_path

    if not valid_target_file:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(target_file):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    
    try:
        with open(target_file, 'r') as f:
            content = f.read(10000)  # Read up to 10,000 characters to prevent excessively large files from being read
            if (f.read(1)):  # Check if there's more content beyond the limit
                content +=  f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
    except Exception as e:
        return f'Error: An error occurred while reading the file "{file_path}": {str(e)}'

    return content

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the content of a specified file relative to the working directory, up to a maximum of 10,000 characters",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to read, relative to the working directory",
            ),
        },
    ),
)