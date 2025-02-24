import argparse
import ollama
from .agent import Jenova
from .llm_api import query_ollama


def main():
    parser = argparse.ArgumentParser(description='Chat with Jenova')
    subparsers = parser.add_subparsers(dest='pipeline')

    command_parser = subparsers.add_parser('command', help='Use the command pipeline')
    command_parser.add_argument('prompt', type=str, help='The prompt to send to Ollama')
    command_parser.add_argument('--model', type=str, default='test', help='The model to use')
    command_parser.add_argument('--verbose', action="store_true", help='Return verbose responses with system_message, prompt, and response')

    question_parser = subparsers.add_parser('question', help='Use the question pipeline')
    question_parser.add_argument('prompt', type=str, help='The prompt to send to Ollama')
    question_parser.add_argument('--model', type=str, default='test', help='The model to use')
    question_parser.add_argument('--verbose', action="store_true", help='Return verbose responses with system_message, prompt, and response')
    # parser.add_argument('--system-message', default=None, help='The system message to send to Ollama')
    args = parser.parse_args()

    jenova = Jenova()
    jenova.setup()


    if args.pipeline == "command":
        tools = jenova.promptify_tools()
        prompt = args.prompt + "\n" + tools

        system_message = "You are an AI agent. From the following list of tools in the Toolbox, choose which one the user is requesting. Respond only with the name of the tool. Respond with 'UNKNOWN' if the user's request is not in the Toolbox."


        command = query_ollama(args.model, prompt, system_message, args.verbose)
        command = command.strip()

        result = [tool for tool in jenova.tools if tool["name"] == command]

        if len(result) == 1:
            result[0]['action']()
        elif len(result) > 1:
            print("Error with toolbox")
        else:
            print("Unknown command")

    elif args.pipeline == "question":
        prompt = args.prompt
        relevant_memory = jenova.get_relevant_memory(prompt)
        recent_memory = jenova.get_recent_memory()
        prompt_with_memory = prompt + "\n\n" + recent_memory + "\n" + relevant_memory

        system_message = """You are a helpful assistant. 
Your job is to answer questions for the user. 
You are given HISTORY for relevant previous conversations and RECENT_CONVERSATION for the most recent conversations. 
Do not mention that you are checking HISTORY and RECENT_CONVERSATION. 
Keep your response short and concise.""".replace("\n", " ")
        response = query_ollama(args.model, prompt_with_memory, system_message, args.verbose)
        if response:
            jenova.add_memory(prompt, response)
        print(response)

    else:
        print("Expecting either --command or --question. Doing nothing")

if __name__ == "__main__":
    main()
