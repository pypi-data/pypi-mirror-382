
import rubigram
from ... import handlers


class OnMessage:
    def on_message(
            self: "rubigram.Client",
            *args, **kwargs,
    ):
        def MetaHandler(func):
            """
            Decorator to register a function as a handler for message updates.

            Args:
                func: The function to be registered as a handler.

            Returns:
                func: The original function.
            """
            self.add_handler(func, handlers.MessageUpdates(*args, **kwargs))
            return func
        return MetaHandler
