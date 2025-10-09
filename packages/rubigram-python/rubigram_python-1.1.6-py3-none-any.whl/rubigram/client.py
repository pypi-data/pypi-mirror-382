
from typing import Optional, Union, Literal
import logging
from .sessions import SQLiteSession, StringSession
from .parser import Markdown
from .methods import Methods


class Client(Methods):
    """Main client for interacting with the Rubika API."""

    DEFAULT_PLATFORM = {
        'app_name': 'Main',
        'app_version': '4.4.20',
        'platform': 'Web',
        'package': 'web.rubika.ir',
    }

    USER_AGENT = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/102.0.0.0 Safari/537.36'
    )

    API_VERSION = '6'

    def __init__(
        self,
        name: Union[str, StringSession],
        auth: Optional[str] = None,
        private_key: Optional[Union[str, bytes]] = None,
        phone_number: Optional[str] = None,
        user_agent: Optional[str] = None,
        timeout: Union[str, int, float] = 20,
        lang_code: str = 'fa',
        parse_mode: Optional[Literal['html', 'markdown', 'mk']] = None,
        proxy: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        display_welcome: bool = False,
        platform: Literal['Web', 'Android'] = 'Web',
    ) -> None:
        """
        Initializes the Rubika client.

        Parameters:
        - name: Session file name (str) or a StringSession instance.
        - auth: Authentication key (optional).
        - private_key: RSA private key (optional, string or bytes).
        - bot_token: Bot token (optional).
        - phone_number: Phone number (optional).
        - user_agent: User-Agent string (optional, default is Chrome).
        - timeout: Request timeout (seconds, default 20).
        - lang_code: Language code (default 'fa').
        - parse_mode: Message parse mode (html, markdown, mk or None).
        - proxy: Proxy address (e.g. 'http://127.0.0.1:80').
        - logger: Logger object for logging (optional).
        - display_welcome: Display welcome message (default False).
        - platform: Client platform ('Web' or 'Android').

        Errors:
        - ValueError: If inputs are invalid.
        - TypeError: If `name` type is incorrect.
        """
        super().__init__()

        # Set platform
        self.DEFAULT_PLATFORM = self.DEFAULT_PLATFORM.copy()
        if platform.lower() == 'android':
            self.DEFAULT_PLATFORM['platform'] = 'Android'

        # Validate inputs
        if auth and not isinstance(auth, str):
            raise ValueError('auth parameter must be a string.')
        if phone_number and not isinstance(phone_number, str):
            raise ValueError('phone_number parameter must be a string.')
        if user_agent and not isinstance(user_agent, str):
            raise ValueError('user_agent parameter must be a string.')
        if not isinstance(timeout, (int, float)):
            try:
                timeout = float(timeout)
            except (ValueError, TypeError):
                raise ValueError('timeout parameter must be a number.')

        # Setup session
        if isinstance(name, str):
            session = SQLiteSession(name)
        elif isinstance(name, StringSession):
            session = name
        else:
            raise TypeError(
                'name parameter must be a string or StringSession instance.')

        # Setup parse_mode
        valid_parse_modes = {'html', 'markdown', 'mk'}
        if parse_mode is not None:
            parse_mode = parse_mode.lower()
            if parse_mode not in valid_parse_modes:
                raise ValueError(
                    f'parse_mode must be one of {valid_parse_modes} or None.')
        else:
            parse_mode = 'markdown'

        # Setup logger
        if not isinstance(logger, logging.Logger):
            logger = logging.getLogger(__name__)

        # Setup private key
        if isinstance(private_key, str):
            if not private_key.startswith('-----BEGIN RSA PRIVATE KEY-----'):
                private_key = f'-----BEGIN RSA PRIVATE KEY-----\n{private_key}'
            if not private_key.endswith('\n-----END RSA PRIVATE KEY-----'):
                private_key += '\n-----END RSA PRIVATE KEY-----'

        # Initialize variables
        self.name = name
        self.auth = auth
        self.logger = logger
        self.private_key = private_key
        self.phone_number = phone_number
        self.display_welcome = display_welcome
        self.user_agent = user_agent or self.USER_AGENT
        self.lang_code = lang_code
        self.timeout = timeout
        self.session = session
        self.parse_mode = parse_mode
        self.proxy = proxy
        self.markdown = Markdown()
        self.database = None
        self.decode_auth = None
        self.import_key = None
        self.is_sync = False
        self.guid = None
        self.key = None
        self.handlers = {}
        self.DEFAULT_PLATFORM['lang_code'] = lang_code

        # Optional welcome message
        if display_welcome:
            self.logger.info("Rubika client initialized successfully.")

    def __enter__(self) -> "Client":
        """Support for context manager to start client."""
        return self.start()

    def __exit__(self, *args, **kwargs) -> None:
        """Support for context manager to disconnect."""
        try:
            self.disconnect()
        except Exception as e:
            self.logger.warning(f"Error while disconnecting: {e}")

    async def __aenter__(self) -> "Client":
        """Support for async context manager to start client."""
        return await self.start()

    async def __aexit__(self, *args, **kwargs) -> None:
        """Support for async context manager to disconnect."""
        try:
            await self.disconnect()
        except Exception as e:
            self.logger.warning(f"Error while disconnecting: {e}")
