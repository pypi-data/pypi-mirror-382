import shadigram
from ... import handlers


class OnShowNotifications:
    def on_show_notifications(
            self: "shadigram.Client",
            *args, **kwargs,
    ):
        def MetaHandler(func):
            self.add_handler(func, handlers.ShowNotifications(*args, **kwargs))
            return func
        return MetaHandler
