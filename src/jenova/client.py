import argparse
import asyncio, json
from jenova.utils.dataclass import Message

def agent_message(type, payload):
    async def tcp_client():
        reader, writer = await asyncio.open_connection('127.0.0.1', 8889)

        message = Message(type=type, payload=payload)

        print(f"Sending: {message}")
        writer.write(message.to_json().encode())
        await writer.drain()

        data = await reader.read(1024)
        response = json.loads(data.decode())
        print(f"Received: {response}")

        writer.close()
        await writer.wait_closed()

    asyncio.run(tcp_client())


def main():
    parser = argparse.ArgumentParser(description='Chat with Jenova')
    parser.add_argument('type', type=str, help='Type of message')
    parser.add_argument('payload', type=str, help='Payload for message')

    args = parser.parse_args()

    agent_message(args.type, args.payload)


if __name__ == "__main__":
    main()
