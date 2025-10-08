from typing import Any


renderers: dict[str, Any] = {}


def renderer(name: str):
    def decorator(func):
        # global renderers
        renderers[name] = func
        return func
    return decorator
