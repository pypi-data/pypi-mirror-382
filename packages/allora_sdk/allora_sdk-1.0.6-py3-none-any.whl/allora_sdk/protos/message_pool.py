
from betterproto2 import Message

def get_type_url(package_name: str, message_name: str) -> str:
    return f"/{package_name}.{message_name}"


class MessagePool:
    def __init__(self):
        self.url_to_type: dict[str, type[Message]] = {}
        self.type_to_url: dict[type[Message], str] = {}

    def register_message(self, package_name: str, message_name: str, message_type: "type[Message]") -> None:
        url = get_type_url(package_name, message_name)

        if url in self.url_to_type or message_type in self.type_to_url:
            raise RuntimeError(f"the message {package_name}.{message_name} is already registered in the message pool")

        self.url_to_type[url] = message_type
        self.type_to_url[message_type] = url

default_message_pool = MessagePool()
    