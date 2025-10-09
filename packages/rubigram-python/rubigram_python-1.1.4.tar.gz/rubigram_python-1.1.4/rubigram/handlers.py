
import asyncio
import sys
from typing import Type, List, Dict, Any, Optional
from .types import Update

# List of authorized handlers
AUTHORIZED_HANDLERS = [
    'ChatUpdates',
    'EditUpdates',
    'MessageUpdates',
    'ShowActivities',
    'ShowNotifications',
    'RemoveNotifications'
]


def create_handler(
    name: str,
    base: tuple,
    authorized_handlers: List[str] = AUTHORIZED_HANDLERS,
    exception: bool = True,
    **kwargs
) -> Optional[Type['BaseHandlers']]:
    """
    Dynamically create a handler based on its name and base class.

    Parameters:
    - name: Name of the handler.
    - base: Base class for the handler.
    - authorized_handlers: List of authorized handler names.
    - exception: Whether to raise an error if the handler is unauthorized.
    - kwargs: Additional arguments to configure the class.

    Returns:
    - The created handler class or None if unauthorized.

    Raises:
    - AttributeError: If the handler is unauthorized and exception=True.
    """
    if name in authorized_handlers:
        return type(name, base, {'__name__': name, **kwargs})

    if not exception:
        return None

    raise AttributeError(f"Module has no handler named '{name}'")


class BaseHandlers(Update):
    """
    Base class for custom handlers.

    Parameters:
    - models: List of filter models.
    - any_handler: Whether any handler should be executed.
    - kwargs: Additional arguments.
    """
    __name__ = 'CustomHandlers'

    def __init__(
            self,
            *models: Any,
            any_handler: bool = False,
            **kwargs) -> None:
        self.__models = models
        self.__any_handler = any_handler

    def is_async(self, value: Any) -> bool:
        """
        Check if the given function is asynchronous.

        Parameters:
        - value: The function to check.

        Returns:
        - True if the function is async, otherwise False.
        """
        return asyncio.iscoroutinefunction(value) or (
            hasattr(
                value,
                '__call__') and asyncio.iscoroutinefunction(
                value.__call__))

    async def __call__(self, update: Dict, *args, **kwargs) -> bool:
        """
        Execute the handler on the given update.

        Parameters:
        - update: The update dictionary.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - True if the handler should be executed, otherwise False.
        """
        self.original_update = update

        if not self.__models:
            return True

        for handler_filter in self.__models:
            filter_instance = handler_filter(
                func=None) if isinstance(
                handler_filter, type) else handler_filter
            status = await filter_instance(self, result=None) if self.is_async(filter_instance) else filter_instance(self, result=None)

            if status and self.__any_handler:
                return True
            if not status:
                return False

        return True


class Handlers:
    """
    Class for managing and creating custom handlers.
    """

    def __init__(self, name: str) -> None:
        self.__name__ = name

    def __eq__(self, value: object) -> bool:
        """
        Check equality with the base handler class.

        Parameters:
        - value: The object to compare.

        Returns:
        - True if equal to BaseHandlers, otherwise False.
        """
        return BaseHandlers in getattr(value, '__bases__', ())

    def __dir__(self) -> List[str]:
        """
        Get the list of authorized handlers.

        Returns:
        - A sorted list of authorized handlers.
        """
        return sorted(AUTHORIZED_HANDLERS)

    def __call__(self, name: str, *args, **kwargs) -> Type['BaseHandlers']:
        """
        Call a handler by its name.

        Parameters:
        - name: The name of the handler.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - The created handler class.
        """
        return self.__getattr__(name)(*args, **kwargs)

    def __getattr__(self, name: str) -> Type['BaseHandlers']:
        """
        Get a dynamically created handler by its name.

        Parameters:
        - name: The name of the handler.

        Returns:
        - The created handler class.
        """
        return create_handler(name, (BaseHandlers,), AUTHORIZED_HANDLERS)


# Replace the current module with an instance of Handlers
sys.modules[__name__] = Handlers(__name__)

# Handler type definitions
ChatUpdates: Type[BaseHandlers]
MessageUpdates: Type[BaseHandlers]
ShowActivities: Type[BaseHandlers]
ShowNotifications: Type[BaseHandlers]
RemoveNotifications: Type[BaseHandlers]
