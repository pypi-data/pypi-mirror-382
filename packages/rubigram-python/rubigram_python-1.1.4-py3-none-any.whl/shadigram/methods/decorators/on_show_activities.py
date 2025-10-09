import shadigram
from ... import handlers


class OnShowActivities:
    def on_show_activities(
            self: "shadigram.Client",
            *args, **kwargs,
    ):
        def MetaHandler(func):
            self.add_handler(func, handlers.ShowActivities(*args, **kwargs))
            return func
        return MetaHandler
