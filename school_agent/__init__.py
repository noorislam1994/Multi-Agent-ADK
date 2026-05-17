try:
    from . import agent
except ModuleNotFoundError as exc:
    if exc.name != "google.adk":
        raise
    agent = None
