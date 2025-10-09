
import threading
import asyncio
import aiohttp
import aiofiles
import inspect
import rubigram
import os
import logging
from .types import Update
from .crypto import Crypto
from . import exceptions


def capitalize(text: str) -> str:
    """
    Convert snake_case string to CamelCase.

    Parameters:
    - text: String in snake_case format.

    Returns:
    String in CamelCase format.
    """
    return ''.join(word.title() for word in text.split('_'))


class Network:
    HEADERS = {
        'origin': 'https://web.rubika.ir',
        'referer': 'https://web.rubika.ir/',
        'content-type': 'application/json',
        'connection': 'keep-alive'
    }

    def __init__(self, client: "rubpy.Client") -> None:
        """
        Initialize the Network class.

        Parameters:
        - client: An instance of rubpy.Client.
        """
        self.client = client
        self.logger = logging.getLogger(__name__)
        self.headers = self.HEADERS.copy()
        self.headers['user-agent'] = client.user_agent

        if client.DEFAULT_PLATFORM['platform'] == 'Android':
            self.headers.pop('origin', None)
            self.headers.pop('referer', None)
            self.headers['user-agent'] = 'okhttp/3.12.1'
            client.DEFAULT_PLATFORM['package'] = 'ir.rubx.bapp'
            client.DEFAULT_PLATFORM['Host'] = 'messengerg2c6.iranlms.ir'
            client.DEFAULT_PLATFORM['app_version'] = '3.6.4'

        connector = aiohttp.TCPConnector(verify_ssl=False, limit=100)
        self.session = aiohttp.ClientSession(
            connector=connector,
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=client.timeout)
        )

        self.api_url = None
        self.wss_url = None
        self.ws = None

    async def close(self) -> None:
        """
        Close the aiohttp ClientSession.
        """
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_dcs(
            self,
            max_retries: int = 3,
            backoff: float = 1.0) -> bool:
        """
        Fetch API and WebSocket URLs with retry mechanism.

        Returns:
        True if successful.
        """
        for attempt in range(max_retries):
            try:
                async with self.session.get('https://getdcmess.iranlms.ir/', proxy=self.client.proxy) as response:
                    response.raise_for_status()
                    data = (await response.json()).get('data')
                    self.api_url = f"{data['API'][data['default_api']]}/"
                    self.wss_url = data['socket'][data['default_socket']]
                    return True
            except Exception as e:
                self.logger.warning(
                    f"Error fetching Data Centers, attempt {
                        attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(backoff * (2 ** attempt))
        raise exceptions.NetworkError("Failed to fetch Data Centers")

    async def request(
            self,
            url: str,
            data: dict,
            backoff: float = 1.0) -> dict:
        """
        Send HTTP POST request with infinite retry mechanism.

        Parameters:
        - url: API endpoint URL.
        - data: Data to be sent.
        - backoff: Base delay for retries.

        Returns:
        JSON-decoded response.
        """
        attempt = 0
        while True:
            try:
                async with self.session.post(
                    url,
                    json=data,
                    proxy=self.client.proxy
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                attempt += 1
                self.logger.warning(
                    f"Request error, attempt {attempt}: {e}"
                )
                await asyncio.sleep(backoff * (2 ** (attempt - 1)))

    async def send(self, **kwargs) -> dict:
        """
        Send request to Rubika API.

        Parameters:
        - kwargs: parameters for request

        Returns:
        JSON-decoded response.
        """
        api_version = str(kwargs.get('api_version', self.client.API_VERSION))
        auth = kwargs.get('auth', self.client.auth)
        client = kwargs.get('client', self.client.DEFAULT_PLATFORM)
        input_data = kwargs.get('input', {})
        method = kwargs.get('method', 'getUserInfo')
        encrypt = kwargs.get('encrypt', True)
        tmp_session = kwargs.get('tmp_session', False)
        url = kwargs.get('url', self.api_url)

        data = {'api_version': api_version}
        key = 'tmp_session' if tmp_session else 'auth'
        data[key] = auth if tmp_session else self.client.decode_auth

        if api_version == '6':
            data_enc = {
                'client': client,
                'method': method,
                'input': input_data}
            if encrypt:
                data['data_enc'] = Crypto.encrypt(
                    data_enc, key=self.client.key)
                if not tmp_session:
                    data['sign'] = Crypto.sign(
                        self.client.import_key, data['data_enc'])
            return await self.request(url, data)

        elif api_version == '0':
            data.update({'auth': auth, 'client': client,
                        'data': input_data, 'method': method})
        elif api_version == '4':
            data.update({'client': client, 'method': method})
        elif api_version == 'bot':
            return await self.request(f"{self.bot_api_url}{method}", input_data)

        return await self.request(url, data)

    async def handle_update(self, name: str, update: dict) -> None:
        """
        Handle updates for registered handlers.
        """
        for func, handler in self.client.handlers.items():
            try:
                if isinstance(handler, type):
                    handler = handler()

                if handler.__name__ != capitalize(name):
                    continue

                if not await handler(update=update):
                    continue

                update_obj = Update(handler.original_update)
                if not inspect.iscoroutinefunction(func):
                    threading.Thread(target=func, args=(update_obj,)).start()
                else:
                    asyncio.create_task(func(update_obj))
            except exceptions.StopHandler:
                break
            except Exception as e:
                self.logger.error(
                    f"Handler error for {name}: {e}", extra={
                        'data': update}, exc_info=True)

    async def get_updates(self) -> None:
        """
        Receive updates from Rubika WebSocket with reconnection logic.
        """
        asyncio.create_task(self.keep_socket())
        while True:
            try:
                async with self.session.ws_connect(self.wss_url, proxy=self.client.proxy, receive_timeout=5) as ws:
                    self.ws = ws
                    await ws.send_json({'method': 'handShake', 'auth': self.client.auth, 'api_version': '6', 'data': ''})
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            asyncio.create_task(
                                self.handle_text_message(msg.json()))
                        elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                            break
            except (aiohttp.ServerTimeoutError, TimeoutError, aiohttp.ClientError):
                await self.client.type_writer(f"{self.client.BOLD}{self.client.MAGENTA}WebSocket{self.client.CYAN} connection{self.client.RED} lost{self.client.WHITE}. {self.client.YELLOW}Reconnecting{self.client.RESET}", line=True)
                await asyncio.sleep(5)

    async def keep_socket(self) -> None:
        """
        Keep WebSocket connection alive by sending periodic pings.
        """
        while True:
            try:
                await asyncio.sleep(10)
                if self.ws and not self.ws.closed:
                    await self.ws.send_json({})
                    await self.client.get_chats_updates()

            except aiohttp.ServerTimeoutError:
                await self.client.type_writer(f"{self.client.BOLD}{self.client.MAGENTA}WebSocket{self.client.CYAN} connection{self.client.RED} lost{self.client.WHITE}. {self.client.YELLOW}Reconnecting{self.client.RESET}", line=True)
                await asyncio.sleep(5)  # wait before reconnecting

            except TimeoutError:
                await self.client.type_writer(f"{self.client.BOLD}{self.client.MAGENTA}WebSocket{self.client.CYAN} connection{self.client.RED} lost{self.client.WHITE}. {self.client.YELLOW}Reconnecting{self.client.RESET}", line=True)
                await asyncio.sleep(5)  # wait before reconnecting

            except aiohttp.ClientError:
                await self.client.type_writer(f"{self.client.BOLD}{self.client.MAGENTA}WebSocket{self.client.CYAN} connection{self.client.RED} lost{self.client.WHITE}. {self.client.YELLOW}Reconnecting{self.client.RESET}", line=True)
                await asyncio.sleep(5)  # wait before reconnecting

    async def handle_text_message(self, msg_data: dict) -> None:
        """
        Handle text messages received from WebSocket.

        Parameters:
        - msg_data: Parsed JSON data.
        """
        if not (data_enc := msg_data.get('data_enc')):
            self.logger.debug(
                "Key data_enc not found", extra={
                    'data': msg_data})
            return

        try:
            decrypted_data = Crypto.decrypt(data_enc, key=self.client.key)
            user_guid = decrypted_data.pop('user_guid')
            tasks = [
                self.handle_update(
                    name,
                    {**update, 'client': self.client, 'user_guid': user_guid})
                for name, package in decrypted_data.items()
                if isinstance(package, list) for update in package]
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(
                f"Error handling WebSocket: {e}", extra={
                    'data': msg_data}, exc_info=True)

    async def upload_file(
            self,
            file,
            mime: str = None,
            file_name: str = None,
            chunk: int = 1048576,
            callback=None,
            max_retries: int = 5,
            backoff: float = 1.0) -> Update:
        """
        Upload file to Rubika with retry logic.

        Parameters:
        - file: File path or bytes.
        - mime: MIME type of the file.
        - file_name: File name.
        - chunk: Chunk size for upload.
        - callback: Callback for progress.
        - max_retries: Maximum number of retries.
        - backoff: Base delay for retries.

        Returns:
        Update object with file metadata.
        """
        if isinstance(file, str):
            if not os.path.exists(file):
                raise ValueError('File not found at specified path')
            file_name = file_name or os.path.basename(file)
            file_size = os.path.getsize(file)
        elif isinstance(file, bytes):
            if not file_name:
                raise ValueError('File name not specified')
            file_size = len(file)
        else:
            raise TypeError('File must be a path or bytes')

        mime = mime or file_name.split('.')[-1]

        result = await self.client.request_send_file(file_name, file_size, mime)
        file_id, dc_id, upload_url, access_hash_send = result.id, result.dc_id, result.upload_url, result.access_hash_send
        total_parts = (file_size + chunk - 1) // chunk

        async def upload_chunk(data, part_number):
            for attempt in range(max_retries):
                try:
                    async with self.session.post(
                        url=upload_url,
                        headers={
                            'auth': self.client.auth,
                            'file-id': file_id,
                            'total-part': str(total_parts),
                            'part-number': str(part_number),
                            'chunk-size': str(len(data)),
                            'access-hash-send': access_hash_send
                        },
                        data=data,
                        proxy=self.client.proxy
                    ) as response:
                        return await response.json()
                except Exception as e:
                    self.logger.warning(
                        f"Error uploading chunk {part_number}، try {
                            attempt + 1}/{max_retries}: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(backoff * (2 ** attempt))
                    else:
                        raise

        index = 0
        if isinstance(file, str):
            async with aiofiles.open(file, 'rb') as f:
                while index < total_parts:
                    await f.seek(index * chunk)
                    data = await f.read(chunk)
                    result = await upload_chunk(data, index + 1)
                    if result.get('status') == 'ERROR_TRY_AGAIN':
                        result = await self.client.request_send_file(file_name, file_size, mime)
                        file_id, dc_id, upload_url, access_hash_send = result.id, result.dc_id, result.upload_url, result.access_hash_send
                        index = 0
                        continue
                    if callable(callback):
                        try:
                            res = callback(file_size, (index + 1) * chunk)
                            if inspect.isawaitable(res):
                                await res
                        except exceptions.CancelledError:
                            return None
                        except Exception as e:
                            self.logger.error(f"Error in callback: {e}")
                    index += 1
        else:
            while index < total_parts:
                data = file[index * chunk:(index + 1) * chunk]
                result = await upload_chunk(data, index + 1)
                if result.get('status') == 'ERROR_TRY_AGAIN':
                    result = await self.client.request_send_file(file_name, file_size, mime)
                    file_id, dc_id, upload_url, access_hash_send = result.id, result.dc_id, result.upload_url, result.access_hash_send
                    index = 0
                    continue
                if callable(callback):
                    try:
                        res = callback(file_size, (index + 1) * chunk)
                        if inspect.isawaitable(res):
                            await res
                    except exceptions.CancelledError:
                        return None
                    except Exception as e:
                        self.logger.error(f"Error in callback: {e}")
                index += 1

        if result['status'] == 'OK' and result['status_det'] == 'OK':
            return Update({
                'mime': mime,
                'size': file_size,
                'dc_id': dc_id,
                'file_id': file_id,
                'file_name': file_name,
                'access_hash_rec': result['data']['access_hash_rec']
            })
        raise exceptions(result['status_det'])(result)

    async def download(
            self,
            dc_id: int,
            file_id: int,
            access_hash: str,
            size: int,
            chunk: int = 131072,
            callback=None,
            gather: bool = False,
            save_as: str = None,
            max_retries: int = 3,
            backoff: float = 1.0) -> bytes:
        """
        Download file from Rubika.

        Parameters:
        - dc_id: Data center ID.
        - file_id: File ID.
        - access_hash: File access hash.
        - size: Total file size.
        - chunk: Chunk size for download.
        - callback: Callback for progress.
        - gather: Use asyncio.gather for concurrent download.
        - save_as: File save path (if specified).
        - max_retries: Maximum number of retries.
        - backoff: Base delay for retries.

        Returns:
        Downloaded file content (bytes) or saved file path.
        """
        headers = {
            'auth': self.client.auth,
            'access-hash-rec': access_hash,
            'file-id': str(file_id),
            'user-agent': self.client.user_agent
        }
        base_url = f'https://messenger{dc_id}.iranlms.ir'

        async def fetch_chunk(session, start_index, last_index):
            chunk_headers = headers.copy()
            chunk_headers.update(
                {'start-index': str(start_index),
                 'last-index': str(last_index)})
            for attempt in range(max_retries):
                try:
                    async with session.post('/GetFile.ashx', headers=chunk_headers, proxy=self.client.proxy) as response:
                        if response.status != 200:
                            self.logger.warning(
                                f"Download failed with status {
                                    response.status}")
                            return b''
                        return await response.read()
                except Exception as e:
                    self.logger.warning(
                        f"Error downloading chunk {start_index}-{last_index}، تلاش {
                            attempt + 1}/{max_retries}: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(backoff * (2 ** attempt))
                    else:
                        return b''

        async with aiohttp.ClientSession(base_url=base_url, connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            if save_as:
                async with aiofiles.open(save_as, 'wb') as f:
                    start_index = 0
                    while start_index < size:
                        last_index = min(start_index + chunk, size) - 1
                        data = await fetch_chunk(session, start_index, last_index)
                        if not data:
                            break
                        await f.write(data)
                        start_index = last_index + 1
                        if callable(callback):
                            try:
                                if inspect.iscoroutinefunction(callback):
                                    await callback(size, start_index)
                                else:
                                    callback(size, start_index)
                            except Exception as e:
                                self.logger.error(f"Error in callback: {e}")
                return save_as
            else:
                if gather:
                    tasks = [
                        fetch_chunk(
                            session, start, min(start + chunk, size) - 1)
                        for start in range(0, size, chunk)]
                    chunks = await asyncio.gather(*tasks)
                    result = b''.join(filter(None, chunks))
                    if callable(callback):
                        try:
                            if inspect.iscoroutinefunction(callback):
                                await callback(size, len(result))
                            else:
                                callback(size, len(result))
                        except Exception as e:
                            self.logger.error(f"Error in callback: {e}")
                    return result
                else:
                    result = b''
                    start_index = 0
                    while start_index < size:
                        last_index = min(start_index + chunk, size) - 1
                        data = await fetch_chunk(session, start_index, last_index)
                        if not data:
                            break
                        result += data
                        start_index = last_index + 1
                        if callable(callback):
                            try:
                                if inspect.iscoroutinefunction(callback):
                                    await callback(size, len(result))
                                else:
                                    callback(size, len(result))
                            except Exception as e:
                                self.logger.error(f"Error in callback: {e}")
                    return result
