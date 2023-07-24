import json
import requests

from logging import Logger
from typing import Dict, List, Tuple

from botpy import Intents

import os
import sys
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)
from qqbotllm import LLMChatClient


__all__ = ['ERNIEBot']


class ERNIEBot:
    def __init__(
        self: 'ERNIEBot',
        url: str,
        api_key: str,
        secret_key: str,
        headers: Dict[str, str] = {
            'Content-Type': 'application/json'
        }
    ) -> None:
        self.access_token: str = requests.request(
            "POST",
            url=f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}",
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
        ).json().get("access_token")
        self.url = url + self.access_token
        self.headers = headers

    def create_prompt(
        self: 'ERNIEBot',
        prompt: str,
        author_id: str,
        history_dict: Dict[str, List[Tuple[str, str]]]
    ) -> str:
        prompts: List[Dict[str, str]] = []
        if author_id in history_dict:
            history = history_dict[author_id]
            for _prompt, _response in history:
                _prompt = {
                    "role": "user",
                    "content": _prompt
                }
                _response = {
                    "role": "assistant",
                    "content": _response
                }
                prompts.append(_prompt)
                prompts.append(_response)
        prompts.append({
            "role": "user",
            "content": prompt
        })
        prompt = json.dumps(
            {
                "messages": prompts,
            }
        )
        return prompt

    async def __call__(
        self: 'ERNIEBot',
        prompt: str,
        author_id: str,
        history_dict: Dict[str, List[Tuple[str, str]]],
        logger: Logger
    ) -> str:
        prompt = self.create_prompt(prompt, author_id, history_dict)
        logger.info(f'[prompt] {json.loads(prompt)}')
        response = requests.request(
            "POST",
            self.url,
            headers=self.headers,
            data=prompt
        ).json().get('result')
        logger.info(f'[response] {response}')
        return response


if __name__ == '__main__':
    api_key = ''
    secret_key = ''
    appid = ''
    token = ''

    commands_dict = {
        '/一言': ERNIEBot(
            url="https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token=",
            api_key=api_key,
            secret_key=secret_key
        ),
        '/一言T': ERNIEBot(
            url="https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/eb-instant?access_token=",
            api_key=api_key,
            secret_key=secret_key
        ),
        '/BLOOMZ': ERNIEBot(
            url="https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/bloomz_7b1?access_token=",
            api_key=api_key,
            secret_key=secret_key
        )
    }

    reset_commands_dict = {
        '/重置': '记忆已重置。'
    }

    client = LLMChatClient(
        commands_dict,
        reset_commands_dict,
        intents=Intents(
            public_guild_messages=True
        )
    )

    client.run(
        appid=appid,
        token=token
    )
