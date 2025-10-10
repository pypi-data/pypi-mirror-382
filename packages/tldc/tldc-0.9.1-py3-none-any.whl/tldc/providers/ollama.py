import json
import requests
from ..assistant import Assistant, register
from ..constants import SYSTEM_PROMPT
from ..logger import logger

class Ollama(Assistant):
    def __init__(self, model, provider, settings, db, dirtree):
        super().__init__(model, provider, settings, db, dirtree)
        self.url = json.loads(settings)["url"]

    def _call_ollama(self, messages, tools=None):
        data = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        if tools:
            data["tools"] = tools
        try:
            response = requests.post(f"{self.url}/api/chat", json=data)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if tools and response.status_code == 400:
                # Retry without tools
                data_no_tools = data.copy()
                del data_no_tools['tools']
                response = requests.post(f"{self.url}/api/chat", json=data_no_tools)
                response.raise_for_status()
                return response.json()
            else:
                raise

    def prompt(self, prompt):
        # Load history
        messages = []
        for row in self.db.get_history(self.dirtree.cwd):
            messages.append(json.loads(row['message']))
        # If no history, add system prompt
        if not messages:
            messages.append({"role": "system", "content": SYSTEM_PROMPT})
        # Add user prompt
        user_msg = {"role": "user", "content": prompt}
        messages.append(user_msg)
        self.db.add_history(self.dirtree.cwd, json.dumps(user_msg))
        # Chat loop for tools
        while True:
            tools = [self._format_tool(t) for t in self.tool_definitions]
            response_data = self._call_ollama(messages, tools=tools)
            message = response_data["message"]
            messages.append(message)
            self.db.add_history(self.dirtree.cwd, json.dumps(message))
            if "tool_calls" in message:
                if message.get("content"):
                    logger(f"Superfluous message content: {message['content']}")
                tool_results = []
                for tool_call in message["tool_calls"]:
                    function_name = tool_call["function"]["name"]
                    function_args = tool_call["function"]["arguments"]
                    if isinstance(function_args, str):
                        function_args = json.loads(function_args)
                    request = self.request_classes[function_name](**function_args)
                    result = json.dumps(self.tools_map[function_name](self, request))
                    tool_msg = {
                        "role": "tool",
                        "content": result,
                        "tool_call_id": tool_call["id"]
                    }
                    tool_results.append(tool_msg)
                for tool_msg in tool_results:
                    messages.append(tool_msg)
                    self.db.add_history(self.dirtree.cwd, json.dumps(tool_msg))
            else:
                return message["content"]

    def _format_tool(self, tool_def):
        return {
            "type": "function",
            "function": {
                "name": tool_def.function.name,
                "description": tool_def.function.description,
                "parameters": tool_def.function.parameters
            }
        }

register("ollama", Ollama)