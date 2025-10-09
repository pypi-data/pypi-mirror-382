import shadigram
from ... import handlers


class OnMessage:
    def on_message(
            self: "shadigram.Client",
            *args, **kwargs,
    ):
        def MetaHandler(func):
            self.add_handler(func, handlers.MessageUpdates(*args, **kwargs))
            return func
        return MetaHandler
