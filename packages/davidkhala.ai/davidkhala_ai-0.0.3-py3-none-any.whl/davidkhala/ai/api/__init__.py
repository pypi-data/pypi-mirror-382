import datetime
from abc import abstractmethod, ABC

import requests

# TODO Think openrouter as exceptional case
class API(ABC):
    def __init__(self, api_key: str, base_url: str):
        self.base_url = base_url+'/v1'
        self.model = None
        self.headers = {
            "Authorization": f"Bearer {api_key}",
        }
    @property
    @abstractmethod
    def free_models(self)->list[str]:
        ...

    def pre_request(self, headers: dict, data: dict):
        data["model"] = self.model
    def chat(self, prompt, system_prompt: str = None):


        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        if system_prompt is not None:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        json = {
            "messages": messages
        }
        self.pre_request(self.headers, json)
        # timeout=50 to cater siliconflow
        response = requests.post(f"{self.base_url}/chat/completions", headers=self.headers, json=json, timeout=50)
        parsed_response = API.parse(response)


        return {
            "data": list(map(lambda x: x['message']['content'], parsed_response['choices'])),
            "meta": {
                "usage": parsed_response['usage'],
                "created": datetime.datetime.fromtimestamp(parsed_response['created'])
            }
        }
    @staticmethod
    def parse(response):
        parsed_response = response.json()

        match parsed_response:
            case dict():
                err = parsed_response.get('error')
                if err is not None:
                    raise Exception(err)
            case str():
                raise Exception(parsed_response)
        return parsed_response
    def list_models(self):
        response = requests.get(f"{self.base_url}/models", headers=self.headers)
        return API.parse(response)['data']