from dataclasses import dataclass
import json

@dataclass
class Message:
    type: str
    payload: str

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(json_str: str) -> "Message":
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return Message(**data)
