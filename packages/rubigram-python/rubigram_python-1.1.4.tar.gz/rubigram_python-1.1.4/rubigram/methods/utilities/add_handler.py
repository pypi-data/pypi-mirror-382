
import inspect
import rubigram
from rubigram import handlers
from typing import Callable, Union


class AddHandler:
    def add_handler(self: "rubigram.Client",
                    func: Callable,
                    handler: Union["handlers.ChatUpdates",
                                   "handlers.MessageUpdates",
                                   "handlers.ShowActivities",
                                   "handlers.ShowNotifications",
                                   "handlers.RemoveNotifications"],
                    ) -> None:
        """
        Add a handler function for updates.

        Args:
        - func (Callable): The handler function to be added.
        - handler (rubigram.handlers.Handler): The handler object.

        Returns:
        - None
        """
        if not inspect.iscoroutinefunction(func):
            self.is_sync = True

        self.handlers[func] = handler
