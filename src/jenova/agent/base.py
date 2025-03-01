from jenova.utils.memory_rag import Rag
import asyncio
import json
from jenova.utils.dataclass import Message, Response
from jenova.utils.llm_api import query_ollama

class BaseAgent():
    def __init__(self, db_name):
        self.tools = []
        self.rag = Rag(db_name)
        self.setup()

    def setup():
        pass

    async def message_dispatcher(self, message):
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
                    result = await self.message_dispatcher(message)
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
                await asyncio.sleep(10)  # Simulate a non-blocking task
        except asyncio.CancelledError:
            print("Other processing task canceled.")
            print("Perform cleanup here")




    def add_tool(self, name, description, action):
        tool = {"name": name, "description": description, "action": action}
        self.tools.append(tool)

    def promptify_tools(self):
        toolbox = "<toolbox>\n"
        for tool in self.tools:
            toolbox += f"<tool>{tool['name']}</tool>\n"
            toolbox += f"\t<description>{tool['description']}</description>\n"
            toolbox += "</toolbox>"

        return toolbox

    def add_conversation(self, prompt, response):
        self.rag.write_conversation(prompt, response)

    def add_memory(self, memory):
        self.rag.write_memory(memory)

    def get_memory(self):
        memory = self.rag.get_memory()
        memory = self.promptify_memory(memory, "memories")
        return memory

    def get_relevant_conversations(self, query):
        conversations = self.rag.search_conversation_by_prompt(query)
        conversations = self.promptify_conversations(conversations, "relevant_conversations")
        return conversations

    def get_recent_conversations(self):
        conversations = self.rag.get_recent_conversations()
        conversations = self.promptify_conversations(conversations, "recent_conversations")
        return conversations

    def promptify_conversations(self, conversations, conversation_title):
        conversation = f"<{conversation_title}>\n"
        for entry in conversations:
            conversation += f"<user>{entry.prompt}</user>\n"
            conversation += f"<assistant>{entry.response}</assistant>\n"
        conversation += f"</{conversation_title}>"
        return conversation

    def promptify_memory(self, memories, memory_title):
        memory = f"<{memory_title}>\n"
        for entry in memories:
            memory += f"<memory>{entry.memory}</memory>\n"
        memory += f"</{memory_title}>"
        return memory

    async def command(self, prompt, model="Test", verbose=False):
        tools = self.promptify_tools()
        prompt_with_tools = prompt + "\n" + tools

        system_message = """You are an AI agent.
From the following list of tools in <toolbox>, choose which one the user is requesting.
Respond only with the name of the tool.
Respond with 'UNKNOWN' if the user's request is not in <toolbox>.""".replace("\n", " ")

        command = query_ollama(model, prompt_with_tools, system_message, verbose)
        command = command.strip()

        result = [tool for tool in self.tools if tool["name"] == command]

        if len(result) == 1:
            if result[0]['name'] == "search_internet":
                await result[0]['action'](prompt)
                return result[0]['name']
            else:
                result[0]['action'](prompt)
                return result[0]['name']
        elif len(result) > 1:
            print("Error with toolbox")
            return None
        else:
            print("Unknown command")
            return None

    def question(self, prompt, model="Test", verbose=False):
        prompt = prompt

        memory = self.get_memory()
        relevant_conversations = self.get_relevant_conversations(prompt)
        recent_conversations = self.get_recent_conversations()
        prompt_with_memory_and_recent_conversations = prompt + "\n\n" + memory + "\n\n" + recent_conversations + "\n" + relevant_conversations

        system_message = """You are a helpful assistant.
Your job is to answer questions for the user.
You are given <memories> for knowledge you have, <relevant_conversations> for relevant previous conversations, and <recent_conversations> for the most recent conversations.
Do not mention that you are checking <memories>, <relevant_conversations>, and <recent_conversations>.
Keep your response short and concise.""".replace("\n", " ")
        response = query_ollama(model, prompt_with_memory_and_recent_conversations, system_message, verbose)
        if response:
            self.add_conversation(prompt, response)
        return response

    def memory_dispatch(self, memory):
        self.add_memory(memory)
        return "Added memory"

    def determine_subject(self, prompt, model="Test", verbose=False):
        # system_message = """Extract the main subject of this entity. Response only with the main subject. Be precise, do not add any additional context""".replace("\n", " ")
        system_message = """Determine what I am trying to search the internet for. Be very precise and do not provide additional context. I need the output to be something I can put into a query""".replace("\n", " ")
        return query_ollama(model, prompt, system_message, verbose)

    def get_answer_from_question_information(self, question, question_information, model="test", verbose=True):
        if question_information == None:
            return "No question information provided"
        system_message = """Determine what the answer to the provided <question> is from the provided <internet_search_information>.
Do not add any additional context.
The information you are being provided is from a webscrape that will likely have too much information. Ignore irrelevant information to the question.""".replace("\n", " ")
        prompt = "<internet_search_information>\n" + question_information + "\n</internet_search_information>"
        prompt += "\n"
        prompt += "<question>\n" + question + "\n</question>"
        return query_ollama(model, prompt, system_message, verbose)


    # def subject_of_inquiry(self, prompt):
    #     import spacy
    #     nlp = spacy.load("en_core_web_sm")
    #
    #     doc = nlp(prompt)
    #     subjects = [chunk.text for chunk in doc.noun_chunks]
    #
    #     return subjects if subjects else "No clear subject found" 


