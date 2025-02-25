from jenova.utils.memory_rag import Rag
import asyncio
import json
from jenova.utils.dataclass import Message, Response
from jenova.utils.llm_api import query_ollama

class BaseAgent():
    def __init__(self):
        self.tools = []
        self.memory = Rag()
        self.setup()

    def setup():
        pass

    def message_dispatcher(self, message):
        print(message)
        response = Response(payload="Default response")
        return response

    def event_loop(self):
        async def handle_client(reader, writer):
            addr = writer.get_extra_info('peername')
            print(f"Connection from {addr}")

            try:
                while True:
                    data = await reader.read(1024)
                    if not data:
                        break
                    message = Message.from_json(data.decode())
                    result = self.message_dispatcher(message)
                    response = Response(payload=result)

                    # TODO: Return a terminating Response
                    if response:
                        writer.write(response.to_json().encode())
                        await writer.drain()
            except asyncio.CancelledError:
                print(f"Connection closed due to cancellation: {addr}")
            except Exception as e:
                print(f"Connection closed due to exception: {e}")
            finally:
                print(f"Connection closed: {addr}")
                writer.close()
                await writer.wait_closed()

                # background_task.cancel()

        async def main():
            background_task = asyncio.create_task(self.other_processing())
            server = await asyncio.start_server(handle_client, '0.0.0.0', 8889)
            addr = server.sockets[0].getsockname()
            print(f"Serving on {addr}")

            async with server:
                try:
                    await server.serve_forever()
                except asyncio.CancelledError:
                    print("Server stopped.")
                    print("Perform cleanup here")
                    background_task.cancel()

        asyncio.run(main())

    async def other_processing(self):
        try:
            while True:
                # Perform some other processing here
                print("Performing other processing...")
                await asyncio.sleep(1)  # Simulate a non-blocking task
        except asyncio.CancelledError:
            print("Other processing task canceled.")
            print("Perform cleanup here")




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

    def get_relevant_conversations(self, query):
        conversations = self.memory.search_prompt_embedding(query)
        # self.memory.search_response_embedding(query)
        conversations = self.promptify_conversations(conversations, "RELEVANT_CONVERSATIONS")
        return conversations

    def get_recent_conversations(self):
        conversations = self.memory.get_recent_conversations()
        conversations = self.promptify_conversations(conversations, "RECENT_CONVERSATIONS")
        return conversations

    def promptify_conversations(self, memory, memory_title):
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
            return result[0]['name']
        elif len(result) > 1:
            print("Error with toolbox")
            return None
        else:
            print("Unknown command")
            return None

    def question(self, prompt, model="Test", verbose=False):
        prompt = prompt
        relevant_memory = self.get_relevant_conversations(prompt)
        recent_memory = self.get_recent_conversations()
        prompt_with_memory = prompt + "\n\n" + recent_memory + "\n" + relevant_memory

        system_message = """You are a helpful assistant. 
Your job is to answer questions for the user. 
You are given RELEVANT_CONVERSATIONS for relevant previous conversations and RECENT_CONVERSATIONS for the most recent conversations. 
Do not mention that you are checking RELEVANT_CONVERSATIONS and RECENT_CONVERSATIONS. 
Keep your response short and concise.""".replace("\n", " ")
        response = query_ollama(model, prompt_with_memory, system_message, verbose)
        if response:
            self.add_memory(prompt, response)
        return response

