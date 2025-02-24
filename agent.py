from memory_rag import Rag

class Jenova():
    def __init__(self):
        self.tools = []
        self.memory = Rag()

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

    def get_memory(self, query):
        memory = self.memory.search_prompt_embedding(query)
        # self.memory.search_response_embedding(query)
        memory = self.promptify_memory(memory)
        return memory


    def promptify_memory(self, memory):
        conversation = "#HISTORY:\n"
        for entry in memory:
            prompt = entry[0].prompt
            response = entry[0].response
            conversation += f"User:{prompt}\n"
            conversation += f"Assistant:{response}\n"
        return conversation
