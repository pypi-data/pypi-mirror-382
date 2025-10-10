from xai_sdk import Client
from xai_sdk.chat import tool_result, user, system
import json
from ..assistant import Assistant, register
from ..constants import SYSTEM_PROMPT
from ..logger import logger

class XAI(Assistant):
    def __init__(self, model, provider, settings, db, dirtree):
        super().__init__(model, provider, settings, db, dirtree)
        self.api_key = json.loads(settings)["api_key"]
        self.client = Client(api_key=self.api_key, timeout=3600)

    def _call_tools(self, response):
        if response.tool_calls:
            results = []
            for tool_call in response.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                request = self.request_classes[function_name](**function_args)
                result = json.dumps(self.tools_map[function_name](self, request))
                results.append(tool_result(result))
            return results
        return None

    def prompt(self, prompt):
        self.db.add_history(self.dirtree.cwd, json.dumps({"role": "user", "content": prompt}))
        response_id = self.db.get_response_id(self.dirtree.cwd)
        response = self._chat(prompt, response_id, None)
        tool_results = self._call_tools(response)
        while tool_results:
            if tool_results and response.content:
                logger(f"Superfluous message content: {response.content}")
            response = self._chat(prompt, response.id, tool_results)
            tool_results = self._call_tools(response)
        self.db.add_history(self.dirtree.cwd, json.dumps({"role": "assistant", "content": response.content}))
        return response.content

    def _chat(self, prompt, response_id, tool_results):
        if response_id:
            chat = self.client.chat.create(
                model=self.model,
                previous_response_id=response_id,
                store_messages=True,
                tools=self.tool_definitions,
                tool_choice="auto"
            )
        else:
            chat = self.client.chat.create(
                model=self.model,
                store_messages=True,
                tools=self.tool_definitions,
                tool_choice="auto"
            )
            chat.append(system(SYSTEM_PROMPT))
        if tool_results:
            for tr in tool_results:
                chat.append(tr)
        else:
            chat.append(user(prompt))
        response = chat.sample()
        self.db.set_response_id(self.dirtree.cwd, response.id)
        return response

register("xai", XAI)