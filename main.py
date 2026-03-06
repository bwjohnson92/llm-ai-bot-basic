import os
import argparse
from dotenv import load_dotenv

from google import genai
from google.genai import types
from prompts import system_prompt
from functions.call_function import available_functions, call_function

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
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    for _ in range(5):
        response = generate_content(client, messages)
        new_messages = check_candidate_property(response)
        messages.extend(new_messages)

        print_info(args, response)
        parsed = parse_response(response, args.verbose)
        if parsed is None:
            break
        messages.append(types.Content(role="user", parts=parsed))
    if _ == 4: #Only get 5 prompts a minute on the free Gemini tier
        print("Reached maximum number of iterations.")
        exit(1)

def check_candidate_property(response):
    if response.candidates is None:
        raise RuntimeError("Response is missing candidates.")
        return
    new_messages = []
    for candidate in response.candidates:
        if candidate.content is None:
            raise RuntimeError("Candidate is missing content.")
            continue
        new_messages.append(candidate.content)
    return new_messages

def parse_response(response, verbose):
    if response.function_calls:
        return call_local_function(response, verbose)
    else:
        print_response(response)
        return None

def call_local_function(response, verbose):
    results = []
    for function_call in response.function_calls:
        function_call_result = call_function(function_call, verbose)
        if function_call_result.parts is None:
            raise RuntimeError("Function call result is missing parts.")
            continue
        if function_call_result.parts[0].function_response is None:
            raise RuntimeError("Function call result is missing function response.")
            continue
        if function_call_result.parts[0].function_response.response is None:
            raise RuntimeError("Function call result is missing function response content.")
            continue

        results.append(function_call_result.parts[0])
        if verbose:
            print(f"-> {function_call_result.parts[0].function_response.response}")
    return results

def print_info(args, response):
    if args.verbose:
        print_prompt(args.user_prompt)
        print_token_usage(response)

def generate_content(client, messages):
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