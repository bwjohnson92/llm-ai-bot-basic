import os
import argparse
from dotenv import load_dotenv

from google import genai
from google.genai import types
from prompts import system_prompt
from functions.call_function import available_functions

GEMINI_MODEL = "gemini-2.5-flash"

def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    if api_key is None:
        raise RuntimeError("GEMINI_API_KEY not found in environment variables.")
        return

    client = genai.Client(api_key=api_key)

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    # Now we can access `args.user_prompt`

    response = generate_response(client, args.user_prompt)

    print_info(args, response)

    parse_response(response)

def parse_response(response):
    if response.function_calls:
        for function_call in response.function_calls:
            print(f"Calling function: {function_call.name}({function_call.args})")
    else:
        print_response(response)

def print_info(args, response):
    if args.verbose:
        print_prompt(args.user_prompt)
        print_token_usage(response)

def generate_response(client, user_prompt):
    messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]
    config = types.GenerateContentConfig(
        system_instruction=system_prompt, 
        temperature=0,
        tools=[available_functions],
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL, 
        contents=messages,
        config=config,
    )
    return response

def print_prompt(prompt):
    print("User prompt: " + prompt)

def print_token_usage(response):
    if response.usage_metadata is None:
        raise RuntimeError("Response is missing usage metadata.")
        return
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

def print_response(response):
    print("Response: " + response.text)

if __name__ == "__main__":
    main()