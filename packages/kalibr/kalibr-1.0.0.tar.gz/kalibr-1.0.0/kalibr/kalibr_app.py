from fastapi import FastAPI
from typing import Callable, Dict

class KalibrApp:
    def __init__(self, title: str = "Kalibr App"):
        self.title = title
        self.app = FastAPI(title=title)
        self.actions: Dict[str, Callable] = {}

    def action(self, name: str, description: str):
        def decorator(func):
            self.actions[name] = func

            async def route(**kwargs):
                return func(**kwargs)

            self.app.post(f"/{name}")(route)
            return func
        return decorator

    def get_fastapi_app(self):
        return self.app

app = None
