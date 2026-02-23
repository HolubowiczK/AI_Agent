import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from functions.call_function import available_functions, call_function

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    # Now we can access `args.user_prompt`

    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError("GEMINI_API_KEY is not set")
    client = genai.Client(api_key=api_key)

    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    for _ in range(20):
        response = client.models.generate_content(model="gemini-2.5-flash", contents=messages, config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt, temperature=0))

        if response.candidates is not None: 
            for candidate in response.candidates:
                messages.append(candidate.content)

        if response.function_calls is not None:
            function_results = []
            for function_call in response.function_calls:
                function_call_result = call_function(function_call, verbose=args.verbose)
                if not function_call_result.parts:
                    raise Exception("Function call result is empty")
                if function_call_result.parts[0].function_response is None:
                    raise Exception("Function call result is empty")
                if function_call_result.parts[0].function_response.response is None:
                    raise Exception("Function call result is empty")

                function_results.append(function_call_result.parts[0])

                messages.append(types.Content(role="user", parts=function_results))
                
                if args.verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")


                #messages.append(function_call_result)
        elif response.usage_metadata is not None:
            if args.verbose:
                print(f"User prompt: {args.user_prompt}")
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
            print("Final response:")
            print(response.text)
            return
        else:
            raise RuntimeError("Usage metadata is not available")
    else:
        print("Maximum number of iterations reached")
        exit(1)
    
if __name__ == "__main__":
    main()
