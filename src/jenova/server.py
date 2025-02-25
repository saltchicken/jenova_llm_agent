from jenova.agent.base import BaseAgent

class Jenova(BaseAgent):
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

    def message_dispatcher(self, message):
        if message.type == 'command':
            result = self.command(message.payload, model="Test", verbose=True)

        if message.type == 'question':
            result = self.question(message.payload, model="Test", verbose=True)

        if result:
            return result


def main():
    jenova = Jenova()
    jenova.event_loop()

