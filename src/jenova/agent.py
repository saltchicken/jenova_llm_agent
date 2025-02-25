from .memory_rag import Rag
import asyncio
import json
from .llm_api import query_ollama

class Jenova():
    def __init__(self):
        self.tools = []
        self.memory = Rag()

    def setup(self):
        def computer_power_off():
            print("turns off computer")
        def computer_reboot():
            print("reboots computer")
        def light_toggle():
            print("toggles lights")

        self.add_tool("computer_power_off", "turns the computer off", computer_power_off)
        self.add_tool("computer_reboot", "reboots the computer", computer_reboot)
        self.add_tool("light_toggle", "toggles the lights of the computer", light_toggle)

    def event_loop(self):
        async def handle_client(reader, writer):
            addr = writer.get_extra_info('peername')
            print(f"Connection from {addr}")

            while True:
                data = await reader.read(1024)
                if not data:
                    break
                message = json.loads(data.decode())
                print(f"Received: {message}")

                if message['type'] == 'command':
                    self.command(message['payload'], model="Test", verbose=False)

                if message['type'] == 'question':
                    self.question(message['payload'], model="Test", verbose=False)


                response = {
                    "type": "response",
                    "payload": f"Received {message['type']} with data: {message['payload']}"
                }

                writer.write(json.dumps(response).encode())
                await writer.drain()

            print(f"Connection closed: {addr}")
            writer.close()
            await writer.wait_closed()

        async def main():
            server = await asyncio.start_server(handle_client, '0.0.0.0', 8889)
            addr = server.sockets[0].getsockname()
            print(f"Serving on {addr}")

            async with server:
                await server.serve_forever()

        asyncio.run(main())





    def add_tool(self, name, description, action):
        tool = {"name": name, "description": description, "action": action}
        self.tools.append(tool)

    def promptify_tools(self):
        toolbox = "#Toolbox\n"
        for i, tool in enumerate(self.tools):
            toolbox += f"{str(i)}. {tool['name']}\n"
            toolbox += f"\t- {tool['description']}"
            toolbox += "\n"

        return toolbox

    def add_memory(self, prompt, response):
        self.memory.write_embedding(prompt, response)

    def get_relevant_memory(self, query):
        memory = self.memory.search_prompt_embedding(query)
        # self.memory.search_response_embedding(query)
        memory = self.promptify_memory(memory, "HISTORY")
        return memory

    def get_recent_memory(self):
        memory = self.memory.get_recent_conversations()
        memory = self.promptify_memory(memory, "RECENT_CONVERSATIONS")
        return memory

    def promptify_memory(self, memory, memory_title):
        conversation = f"#{memory_title}:\n"
        for entry in memory:
            conversation += f"User:{entry.prompt}\n"
            conversation += f"Assistant:{entry.response}\n"
        return conversation

    def command(self, prompt, model="Test", verbose=False):
        tools = self.promptify_tools()
        prompt = prompt + "\n" + tools

        system_message = "You are an AI agent. From the following list of tools in the Toolbox, choose which one the user is requesting. Respond only with the name of the tool. Respond with 'UNKNOWN' if the user's request is not in the Toolbox."


        command = query_ollama(model, prompt, system_message, verbose)
        command = command.strip()

        result = [tool for tool in self.tools if tool["name"] == command]

        if len(result) == 1:
            result[0]['action']()
        elif len(result) > 1:
            print("Error with toolbox")
        else:
            print("Unknown command")

    def question(self, prompt, model="Test", verbose=False):
        prompt = prompt
        relevant_memory = self.get_relevant_memory(prompt)
        recent_memory = self.get_recent_memory()
        prompt_with_memory = prompt + "\n\n" + recent_memory + "\n" + relevant_memory

        system_message = """You are a helpful assistant. 
Your job is to answer questions for the user. 
You are given HISTORY for relevant previous conversations and RECENT_CONVERSATION for the most recent conversations. 
Do not mention that you are checking HISTORY and RECENT_CONVERSATION. 
Keep your response short and concise.""".replace("\n", " ")
        response = query_ollama(model, prompt_with_memory, system_message, verbose)
        if response:
            self.add_memory(prompt, response)
        print(response)

def main():
    jenova = Jenova()
    jenova.setup()
    jenova.event_loop()
