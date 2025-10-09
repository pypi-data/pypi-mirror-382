import shadigram
from ... import handlers


class OnRemoveNotifications:
    def on_remove_notifications(
            self: "shadigram.Client",
            *args, **kwargs,
    ):
        def MetaHandler(func):
            self.add_handler(
                func, handlers.RemoveNotifications(
                    *args, **kwargs))
            return func
        return MetaHandler
