from logging import Logger

from typing import Any, Dict, List
from typing import Callable, Tuple, Coroutine

from botpy import Client
from botpy import logging
from botpy.message import Message
from botpy.types.message import Reference


class LLMChatClient(Client):
    def __init__(
        self: 'LLMChatClient',
        commands_dict: Dict[str, Callable[[str, str, Dict[str, List[Tuple[str, str]]], Logger], Coroutine[Any, Any, str]]],
        reset_commands_dict: Dict[str, str],
        *args: Any,
        **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.logger = logging.get_logger()
        self.commands_dict = commands_dict
        self.reset_commands_dict = reset_commands_dict
        self.history_dict: Dict[str, List[Tuple[str, str]]] = {}

    def add_to_history(
        self: 'LLMChatClient',
        author_id: str,
        prompt: str,
        response: str
    ) -> None:
        if author_id not in self.history_dict:
            self.history_dict[author_id] = [(prompt, response)]
        else:
            self.history_dict[author_id].append((prompt, response))

    async def on_at_message_create(
        self: 'LLMChatClient',
        message: Message
    ) -> None:
        for command, info in self.reset_commands_dict.items():
            command = ' ' + command
            if command in message.content:
                if message.author.id in self.history_dict:
                    del self.history_dict[message.author.id]
                await message.reply(
                    content=info,
                    message_reference=Reference(
                        message_id=message.id,
                        ignore_get_message_error=True
                    )
                )

        for command, func in self.commands_dict.items():
            command = ' ' + command + ' '
            if command in message.content:
                self.logger.info(f'[command] {command}')
                prompt = message.content.split(command)[1].strip()
                response = await func(prompt, message.author.id, self.history_dict, self.logger)
                await message.reply(
                    content=response,
                    message_reference=Reference(
                        message_id=message.id,
                        ignore_get_message_error=True
                    )
                )
                self.add_to_history(message.author.id, prompt, response)
