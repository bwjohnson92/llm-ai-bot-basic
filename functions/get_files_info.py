import os
from google import genai
from google.genai import types

def get_files_info(working_directory, directory="."):
    absolute_path = os.path.abspath(working_directory)

    target_directory = os.path.normpath(os.path.join(absolute_path, directory))

    valid_target_directory = os.path.commonpath([absolute_path, target_directory]) == absolute_path

    if not valid_target_directory:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not os.path.isdir(target_directory):
        return f'Error: "{directory}" is not a directory'
    
    try:
        items = os.listdir(target_directory)
        if not items:
            return f'The directory "{directory}" is empty.'
        
        files_info = []
        for item in items:
            item_path = os.path.join(target_directory, item)
            item_info = {
                "name": item,
                "size": os.path.getsize(item_path),
                "is_dir": os.path.isdir(item_path)
            }
            files_info.append(item_info)

        # Build a formatted string to represent the contents of the directory
        string_to_use = "current" if directory == "." else directory
        result = f"Results for '{string_to_use}' directory:\n"
        for info in files_info:
            result += f" - {info['name']}: file_size={info['size']} bytes, is_dir={info['is_dir']}\n"

        return result
    except Exception as e:
        return f'Error: An error occurred while accessing the directory "{directory}": {str(e)}'

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)

