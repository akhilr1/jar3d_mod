import requests
from termcolor import colored
import time
import json
import os
import logging
from langsmith import Client
from langsmith.run_helpers import traceable
from typing import List, Dict, Any
from utils.logging import log_function, setup_logging
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from config.load_configs import load_config

setup_logging(level=logging.DEBUG)
logger = logging.getLogger(__name__)
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
load_config(config_path)
client = Client()

class BaseModel:
    def __init__(
        self,
        temperature: float,
        model: str,
        json_response: bool,
        prompt_caching: bool = False,
        max_retries: int = 3,
        retry_delay: int = 1,
    ):
        self.temperature = temperature
        self.model = model
        self.json_response = json_response
        self.prompt_caching = prompt_caching
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    # @traceable(run_type="llm",
    #            metadata={"ls_provider": 'anthropic', 'ls_model_name': 'claude-3-5-sonnet-20240620'}
    #            )
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), retry=retry_if_exception_type(requests.RequestException))
    def _make_request(self, url, headers, payload):
        response = requests.post(url, headers=headers, json=payload)
        try:
            response.raise_for_status()
        except requests.HTTPError as http_err:
            error_content = response.content.decode('utf-8')
            print(f'HTTP error occurred: {http_err}\nResponse content: {error_content}')
            raise
        return response.json()
    
    def invoke(self, messages: List[Dict[str, str]], guided_json: Dict[str, Any] = None) -> str:
        pass
    
class OpenAIModel(BaseModel):
    def __init__(self, temperature: float, model: str, json_response: bool, max_retries: int = 3, retry_delay: int = 1):
        super().__init__(temperature, model, json_response, max_retries, retry_delay)
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
        load_config(config_path)
        #self.model_endpoint = 'https://api.openai.com/v1/chat/completions'
        self.model_endpoint = os.getenv('LITELLM_ENDPOINT')
        
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

    # def invoke(self, messages: List[Dict[str, str]]) -> str:
    @traceable(run_type="llm", metadata={"ls_provider": 'openai', 'ls_model_name': 'gpt-4o'})
    def invoke(self, messages: List[Dict[str, str]], guided_json: Dict[str, Any] = None) -> str:
        # Extract system message if present
        system = next((msg["content"] for msg in messages if msg["role"] == "system"), None)
        
        # Prepare messages for the API
        api_messages = []
        for msg in messages:
            if msg["role"] != "system":
                content = msg["content"]
                if self.json_response and msg["role"] == "user":
                    content += "\nYou must respond in JSON format."
                api_messages.append({"role": msg["role"], "content": content})
        
        # Prepare payload with the same structure
        if self.model == "o1-preview" or self.model == "o1-mini":
            # Special handling for o1 models
            if system:
                combined_content = f"{system}\n\n{api_messages[0]['content']}"
            else:
                combined_content = api_messages[0]['content']
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": combined_content
                    }
                ]
            }
        else:
            payload = {
                "model": self.model,
                "messages": [],
                "temperature": self.temperature,
                "stream": False,
            }
            if system:
                payload["messages"].append({"role": "system", "content": system})
            payload["messages"].extend(api_messages)
        
        if self.json_response:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "open_ai_agent",
                    "strict": True,
                    "schema": guided_json
                }
            }

        
        #print(f"DEBUG PAYLOAD: {payload}")
        
        try:
            response_json = self._make_request(self.model_endpoint, self.headers, payload)

            if self.json_response:
                response = json.dumps(json.loads(response_json['choices'][0]['message']['content']))
            else:
                response = response_json['choices'][0]['message']['content']

            return response
        except requests.RequestException as e:
            return json.dumps({"error": f"Error in invoking model after {self.max_retries} retries: {str(e)}"})
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Error processing response: {str(e)}"})
    
    # return _invoke()


