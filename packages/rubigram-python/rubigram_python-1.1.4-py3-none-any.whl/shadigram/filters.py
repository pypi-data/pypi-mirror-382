from typing import Union, List, Pattern, Type
import difflib
import inspect
import warnings
import sys
import re

# List of public elements to be exported
__all__ = [
    'Operator',
    'BaseModel',
    'author_guids',
    'object_guids',
    'command',
    'regex',
]
# List of models for internal use
__models__ = [
    'pinned_message', 'mute', 'count_unseen', 'message_id',
    'is_group', 'is_private', 'is_channel', 'is_in_contact',
    'text', 'original_update',
    'time', 'reply_message_id', 'is_me', 'is_forward', 'is_text',
    'music', 'file', 'photo', 'sticker', 'video', 'voice',
    'contact', 'location', 'poll', 'gif', 'is_event', 'is_edited']


def create_model(
        name,
        base,
        authorize: list = [],
        exception: bool = True,
        *args,
        **kwargs):
    """
    Create a model dynamically based on the given name and base class.

    :param name: Name of the model.
    :param base: Base class for the model.
    :param authorize: List of authorized model names.
    :param exception: Whether to raise an exception if the model is not authorized.
    :param args: Additional positional arguments.
    :param kwargs: Additional keyword arguments.
    :return: Dynamically created model class.
    """
    result = None
    if name in authorize:
        result = name
    else:
        proposal = difflib.get_close_matches(name, authorize, n=1)
        if proposal:
            result = proposal[0]
            caller = inspect.getframeinfo(inspect.stack()[2][0])
            warnings.warn(
                f'{caller.filename}:{caller.lineno}: Do you mean'
                f' "{name}", "{result}"? Correct it.')

    if result is not None or not exception:
        if result is None:
            result = name
        return type(result, base, {'__name__': result, **kwargs})

    raise AttributeError(f'Module has no attribute ({name})')


class Operator:
    """
    Class representing operators used in filtering models.
    """
    Or = 'OR'
    And = 'AND'
    Less = 'Less'
    Lesse = 'Lesse'
    Equal = 'Equal'
    Greater = 'Greater'
    Greatere = 'Greatere'
    Inequality = 'Inequality'

    def __init__(self, value, operator, *args, **kwargs):
        self.value = value
        self.operator = operator

    def __eq__(self, value) -> bool:
        return self.operator == value


class BaseModel:
    """
    Base class for custom models.
    """

    def __init__(self, func=None, filters=[], *args, **kwargs) -> None:
        self.func = func
        if not isinstance(filters, list):
            filters = [filters]
        self.filters = filters

    def insert(self, filter):
        self.filters.append(filter)
        return self

    def __or__(self, value):
        return self.insert(Operator(value, Operator.Or))

    def __and__(self, value):
        return self.insert(Operator(value, Operator.And))

    def __eq__(self, value):
        return self.insert(Operator(value, Operator.Equal))

    def __ne__(self, value):
        return self.insert(Operator(value, Operator.Inequality))

    def __lt__(self, value):
        return self.insert(Operator(value, Operator.Less))

    def __le__(self, value):
        return self.insert(Operator(value, Operator.Lesse))

    def __gt__(self, value):
        return self.insert(Operator(value, Operator.Greater))

    def __ge__(self, value):
        return self.insert(Operator(value, Operator.Greatere))

    async def build(self, update):
        result = getattr(update, self.__class__.__name__, None)
        if callable(self.func):
            if update.is_async(self.func):
                result = await self.func(result)
            else:
                result = self.func(result)

        for filter in self.filters:
            value = filter.value

            if callable(value):
                if update.is_async(value):
                    value = await value(update, result)
                else:
                    value = value(update, result)

            if self.func:
                if update.is_async(self.func):
                    value = await self.func(value)
                else:
                    value = self.func(value)

            if filter == Operator.Or:
                result = result or value
            elif filter == Operator.And:
                result = result and value
            elif filter == Operator.Less:
                result = result < value
            elif filter == Operator.Lesse:
                result = result <= value
            elif filter == Operator.Equal:
                result = result == value
            elif filter == Operator.Greater:
                result = result > value
            elif filter == Operator.Greatere:
                result = result >= value
            elif filter == Operator.Inequality:
                result = result != value

        return bool(result)

    async def __call__(self, update, *args, **kwargs):
        return await self.build(update)


class command(BaseModel):
    """
    Filter for commands in text messages.
    """

    def __init__(
            self,
            commands: Union[str, List[str]],
            prefixes: Union[str, List[str]] = '',
            case_sensitive: bool = False, *args, **kwargs,
    ) -> None:
        """Filter Commands, i.e.: text messages starting with "/" or any other custom prefix.

        Parameters:
            commands (``str`` | ``list``):
                The command or list of commands as string the filter should look for.
                Examples: "start", ["start", "help", "settings"]. When a message text containing
                a command arrives, the command itself and its arguments will be stored in the *command*
                field of the :obj:`~pyrogram.types.Message`.

            prefixes (``str`` | ``list``, *optional*):
                A prefix or a list of prefixes as string the filter should look for.
                Defaults to "" (slash). Examples: ".", "!", ["/", "!", "."], list(".:!").
                Pass None or "" (empty string) to allow commands with no prefix at all.

            case_sensitive (``bool``, *optional*):
                Pass True if you want your command(s) to be case sensitive. Defaults to False.
                Examples: when True, command="Start" would trigger /Start but not /start.
        """

        super().__init__(*args, **kwargs)
        self.command_re = re.compile(r"([\"'])(.*?)(?<!\\)\1|(\S+)")
        commands = commands if isinstance(commands, list) else [commands]
        commands = {c if case_sensitive else c.lower() for c in commands}

        prefixes = [] if prefixes is None else prefixes
        prefixes = prefixes if isinstance(prefixes, list) else [prefixes]
        prefixes = set(prefixes) if prefixes else {""}

        self.commands = commands
        self.prefixes = prefixes
        self.case_sensitive = case_sensitive

    async def __call__(self, update, *args, **kwargs) -> bool:
        username = ""
        text = update.text
        update['command'] = None

        if not text:
            return False

        for prefix in self.prefixes:
            if not text.startswith(prefix):
                continue

            without_prefix = text[len(prefix):]

            for cmd in self.commands:
                if not re.match(
                    rf"^(?:{cmd}(?:@?{username})?)(?:\s|$)",
                    without_prefix,
                        flags=re.IGNORECASE if not self.case_sensitive else 0):
                    continue

                without_command = re.sub(
                    rf"{cmd}(?:@?{username})?\s?", "", without_prefix, count=1,
                    flags=re.IGNORECASE if not self.case_sensitive else 0)

                # match.groups are 1-indexed, group(1) is the quote, group(2) is the text
                # between the quotes, group(3) is unquoted, whitespace-split
                # text

                # Remove the escape character from the arguments
                update['command'] = [cmd] + [
                    re.sub(r"\\([\"'])", r"\1", m.group(2) or m.group(3) or "")
                    for m in self.command_re.finditer(without_command)
                ]

                return True

        return False


class regex(BaseModel):
    """
    Filter for matching text using regular expressions.
    """

    def __init__(self, pattern: Pattern, *args, **kwargs) -> None:
        self.pattern = re.compile(pattern)
        super().__init__(*args, **kwargs)

    async def __call__(self, update, *args, **kwargs) -> bool:
        if update.text is None:
            return False

        update.pattern_match = self.pattern.match(update.text)
        return bool(update.pattern_match)


class object_guids(BaseModel):
    """
    Filter based on object GUIDs.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.object_guids = []
        for arg in args:
            if isinstance(arg, list):
                self.object_guids.extend(arg)
            elif isinstance(arg, tuple):
                self.object_guids.extend(list(arg))
            else:
                self.object_guids.append(arg)

    async def __call__(self, update, *args, **kwargs) -> bool:
        return update.object_guid is not None and update.object_guid in self.object_guids


class author_guids(BaseModel):
    """
    Filter based on author GUIDs.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.author_guids = []
        for arg in args:
            if isinstance(arg, list):
                self.author_guids.extend(arg)
            elif isinstance(arg, tuple):
                self.author_guids.extend(list(arg))
            else:
                self.author_guids.append(arg)

    async def __call__(self, update, *args, **kwargs) -> bool:
        return update.author_guid is not None and update.author_guid in self.author_guids


class Models:
    """
    Class to handle and create specific models.
    """

    def __init__(self, name, *args, **kwargs) -> None:
        self.__name__ = name

    def __eq__(self, value: object) -> bool:
        return BaseModel in value.__bases__

    def __dir__(self):
        return sorted(__models__)

    def __call__(self, name, *args, **kwargs):
        return self.__getattr__(name)

    def __getattr__(self, name):
        if name in __all__:
            return globals()[name]
        return create_model(
            name, (BaseModel,),
            authorize=__models__, exception=False)


# Replace the current module with an instance of Models
sys.modules[__name__] = Models(__name__)

# Define specific model types
pinned_message: Type[BaseModel]
mute: Type[BaseModel]
count_unseen: Type[BaseModel]
message_id: Type[BaseModel]
is_group: Type[BaseModel]
is_private: Type[BaseModel]
is_channel: Type[BaseModel]
is_in_contact: Type[BaseModel]
edited: Type[BaseModel]
text: Type[BaseModel]
original_update: Type[BaseModel]
time: Type[BaseModel]
reply_message_id: Type[BaseModel]
is_me: Type[BaseModel]
forward: Type[BaseModel]
event: Type[BaseModel]
is_text: Type[BaseModel]
music: Type[BaseModel]
file: Type[BaseModel]
photo: Type[BaseModel]
video: Type[BaseModel]
voice: Type[BaseModel]
contact: Type[BaseModel]
location: Type[BaseModel]
poll: Type[BaseModel]
gif: Type[BaseModel]
sticker: Type[BaseModel]
is_event: Type[BaseModel]
