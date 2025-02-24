from .memory_rag import Rag

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
