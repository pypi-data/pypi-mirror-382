from typing import TypedDict, Optional

from davidkhala.ai.api import API


class Leaderboard(TypedDict):
    url:Optional[str]
    name:Optional[str]

class OpenRouter(API):
    @property
    def free_models(self) -> list[str]:
        return list(
            map(lambda model: model['id'],
                filter(lambda model: model['id'].endswith(':free'), self.list_models())
                )
        )

    def __init__(self, api_key: str, models: list[str] = None, *,
                 leaderboard: Leaderboard = None):

        super().__init__(api_key, 'https://openrouter.ai/api')
        self.leaderboard = leaderboard
        if models is None:
            models = [self.free_models[0]]
        self.models = models

    def pre_request(self, headers: dict, data: dict):
        if self.leaderboard is not None:
            headers["HTTP-Referer"] = self.leaderboard['url'],  # Optional. Site URL for rankings on openrouter.ai.
            headers["X-Title"] = self.leaderboard['name'],  # Optional. Site title for rankings on openrouter.ai.
        if len(self.models) > 1:
            data["models"] = self.models
        else:
            data["model"] = self.models[0]
