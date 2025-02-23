import argparse
import ollama
from agent import Jenova

def query_ollama(model, prompt, system_message=None):
    ollama.api_host = "http://localhost:11434"
    messages = [{"role": "user", "content": prompt}]
    if system_message:
        messages.insert(0,{"role": "system", "content": system_message})

    pretty_print_prompt(prompt, system_message)

    response = ollama.chat(
        model=model,  # Replace with the model you're using
        messages=messages
    )

    return response['message']['content']

def pretty_print_prompt(prompt, system_message):
    print(system_message)
    print(prompt)

def main():
    parser = argparse.ArgumentParser(description='Chat with Ollama')
    parser.add_argument('prompt', type=str, help='The prompt to send to Ollama')
    parser.add_argument('--model', type=str, default='test', help='The model to use')
    parser.add_argument('--command', action="store_true", help='Make a call to the agent')
    parser.add_argument('--question', action="store_true", help='Ask a question')
    # parser.add_argument('--system-message', default=None, help='The system message to send to Ollama')
    args = parser.parse_args()

    jenova = Jenova()

    def dummy():
        print("Hello")

    jenova.add_tool("computer_power_off", "turns the computer off", dummy)
    jenova.add_tool("computer_reboot", "reboots the computer", dummy)
    jenova.add_tool("light_toggle", "toggles the lights of the computer", dummy)

    if args.command:
        tools = jenova.promptify_tools()
        prompt = args.prompt + "\n" + tools

        system_message = "You are an AI agent. From the following list of tools in the Toolbox, choose which one the user is requesting. Respond only with the name of the tool. Respond with 'UNKNOWN' if the user's request is not in the Toolbox."


        command = query_ollama(args.model, prompt, system_message)
        print(command)

        result = [tool for tool in jenova.tools if tool["name"] == command]

        if len(result) == 1:
            result[0]['action']()
        elif len(result) > 1:
            print("Error with toolbox")
        else:
            print("Unknown command")

    elif args.question:
        prompt = args.prompt
        system_message = "You are a helpful assistant. Your job is to answer questions for the user."
        response = query_ollama(args.model, prompt, system_message)
        if response:
            jenova.add_memory(prompt, response)
        print(response)

    else:
        print("Expecting either --command or --question. Doing nothing")



if __name__ == "__main__":
    main()
