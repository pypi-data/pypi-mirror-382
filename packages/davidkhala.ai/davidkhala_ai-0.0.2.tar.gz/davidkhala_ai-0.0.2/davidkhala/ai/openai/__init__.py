import runpy
from typing import Union, Literal, List

from openai import OpenAI, AsyncOpenAI

from davidkhala.ai.model import AbstractClient


class Client(AbstractClient):
    client: OpenAI
    encoding_format: Literal["float", "base64"] = "float"

    def connect(self):
        self.client.models.list()

    def encode(self, *_input: str) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.model,
            input=list(_input),
            encoding_format=self.encoding_format
        )
        return [item.embedding for item in response.data]

    def chat(self, user_prompt, image: str = None):

        message = {
            "role": "user"
        }
        if image is None:
            message['content'] = user_prompt
        else:
            message['content'] = [
                {"type": "text", "text": user_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image,
                    }
                },
            ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                *self.messages,
                message
            ],
        )
        return response.choices[0].message.content

    def disconnect(self):
        self.client.close()


def with_opik(instance: Union[OpenAI, AsyncOpenAI]):
    from opik.integrations.openai import track_openai
    runpy.run_path('../opik.py')
    return track_openai(instance)
