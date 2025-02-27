from jenova.agent.base import BaseAgent
from jenova.utils.internet_search import search_engine_crawler

class Jenova(BaseAgent):
    def setup(self):
        def computer_power_off(prompt=None):
            print("turns off computer")
        def computer_reboot(prompt=None):
            print("reboots computer")
        def light_toggle(prompt=None):
            print("toggles lights")
        async def search_internet(prompt):
            subject = self.determine_subject(prompt)
            print(f"Searching internet for {subject}")
            question_information = await search_engine_crawler(subject)

            if question_information is None:
                print("Unable to determine question information")
                return "Unable to search for answer"
            answer = self.get_answer_from_question_information(subject, question_information)
            print(f"ANSWER: {answer}")
            # ddgo = duckduckgo_instant_answer(subject)
            # if ddgo:
            #     print(f"DUCKDUCK: {ddgo}")
            # else:
            #     print("DUCKDUCK unable to determine via instant answer")

        self.add_tool("computer_power_off", "turns the computer off", computer_power_off)
        self.add_tool("computer_reboot", "reboots the computer", computer_reboot)
        self.add_tool("light_toggle", "toggles the lights of the computer", light_toggle)
        self.add_tool("search_internet", "searches the internet for information that I may not know", search_internet)

    async def message_dispatcher(self, message):
        if message.type == 'command':
            result = await self.command(message.payload, model="Test", verbose=True)

        if message.type == 'question':
            result = self.question(message.payload, model="Test", verbose=True)

        if message.type == 'memory':
            result = self.memory_dispatch(message.payload)
            return None

        if result:
            return result


def main():
    jenova = Jenova("jenova")
    jenova.event_loop()

