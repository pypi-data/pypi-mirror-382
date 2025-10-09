import asyncio
import dataclasses
import aiohttp
from aiohttp import web
import json
from typing import Callable, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import os
from collections import deque
import time
import uuid

# Setup logging
logging.basicConfig()
logger = logging.getLogger(__name__)

# Enums


class UpdateTypeEnum(str, Enum):
    NEW_MESSAGE = "NewMessage"
    UPDATED_MESSAGE = "UpdatedMessage"
    REMOVED_MESSAGE = "RemovedMessage"
    STARTED_BOT = "StartedBot"
    STOPPED_BOT = "StoppedBot"
    UPDATED_PAYMENT = "UpdatedPayment"


class ChatKeypadTypeEnum(str, Enum):
    NONE = "None"
    NEW = "New"
    REMOVE = "Remove"


class ButtonTypeEnum(str, Enum):
    SIMPLE = "Simple"
    SELECTION = "Selection"
    CALENDAR = "Calendar"
    NUMBER_PICKER = "NumberPicker"
    STRING_PICKER = "StringPicker"
    LOCATION = "Location"
    PAYMENT = "Payment"
    CAMERA_IMAGE = "CameraImage"
    CAMERA_VIDEO = "CameraVideo"
    GALLERY_IMAGE = "GalleryImage"
    GALLERY_VIDEO = "GalleryVideo"
    FILE = "File"
    AUDIO = "Audio"
    RECORD_AUDIO = "RecordAudio"
    MY_PHONE_NUMBER = "MyPhoneNumber"
    MY_LOCATION = "MyLocation"
    TEXTBOX = "Textbox"
    LINK = "Link"
    ASK_MY_PHONE_NUMBER = "AskMyPhoneNumber"
    ASK_LOCATION = "AskLocation"
    BARCODE = "Barcode"

# Data Models


@dataclass
class Button:
    id: str
    type: ButtonTypeEnum
    button_text: str
    button_selection: Optional[Dict] = None
    button_calendar: Optional[Dict] = None
    button_number_picker: Optional[Dict] = None
    button_string_picker: Optional[Dict] = None
    button_location: Optional[Dict] = None
    button_textbox: Optional[Dict] = None


@dataclass
class KeypadRow:
    buttons: List[Button]


@dataclass
class MessageId:
    message_id: Optional[str] = None


@dataclass
class Keypad:
    rows: List[KeypadRow]
    resize_keyboard: bool = True
    on_time_keyboard: bool = False


@dataclass
class Message:
    message_id: str
    text: str
    time: str
    is_edited: bool
    sender_type: str
    sender_id: str
    aux_data: Optional[Dict] = None
    file: Optional[Dict] = None
    reply_to_message_id: Optional[str] = None
    forwarded_from: Optional[Dict] = None
    location: Optional[Dict] = None
    sticker: Optional[Dict] = None
    contact_message: Optional[Dict] = None
    poll: Optional[Dict] = None
    live_location: Optional[Dict] = None


@dataclass
class Update:
    type: UpdateTypeEnum
    chat_id: str
    client: Optional["BotClient"] = None
    removed_message_id: Optional[str] = None
    new_message: Optional[Message] = None
    updated_message: Optional[Message] = None
    updated_payment: Optional[Dict] = None

    async def reply(
        self,
        text: str,
        chat_keypad: Optional[Keypad] = None,
        inline_keypad: Optional[Keypad] = None,
        disable_notification: bool = False,
        chat_keypad_type: ChatKeypadTypeEnum = ChatKeypadTypeEnum.NONE,
        chat_id: str = None
    ) -> Dict:
        if not self.client:
            raise ValueError("Client not set for Update")
        return await self.client.send_message(
            chat_id=chat_id or self.chat_id,
            text=text,
            chat_keypad=chat_keypad,
            inline_keypad=inline_keypad,
            disable_notification=disable_notification,
            reply_to_message_id=self.new_message.message_id if self.new_message else None,
            chat_keypad_type=chat_keypad_type
        )


@dataclass
class InlineMessage:
    sender_id: str
    text: str
    message_id: str
    chat_id: str
    file: Optional[Dict] = None
    location: Optional[Dict] = None
    aux_data: Optional[Dict] = None

# Filters


class Filter:
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        return True


class TextFilter(Filter):
    def __init__(self, text: str, regex: bool = False):
        self.text = text
        self.regex = regex

    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        import re
        text = update.new_message.text if isinstance(
            update, Update) and update.new_message else update.text if isinstance(
            update, InlineMessage) else ""
        if not text:
            return False
        return bool(
            re.match(
                self.text,
                text)) if self.regex else text == self.text


class CommandFilter(Filter):
    def __init__(self, command: Union[str, List[str]]):
        self.commands = [command] if isinstance(command, str) else command

    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        text = update.new_message.text if isinstance(
            update, Update) and update.new_message else update.text if isinstance(
            update, InlineMessage) else ""
        if not text:
            return False
        return any(text.startswith(f"/{cmd}") for cmd in self.commands)


class ButtonFilter(Filter):
    def __init__(self, button_id: str):
        self.button_id = button_id

    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        aux_data = None
        update_type = "InlineMessage" if isinstance(
            update, InlineMessage) else update.type
        if isinstance(
                update, Update) and (
                update.new_message or update.updated_message):
            message = update.new_message or update.updated_message
            aux_data = message.aux_data
        elif isinstance(update, InlineMessage):
            aux_data = update.aux_data

        if not aux_data:
            logger.info(
                f"No aux_data for button_id={self.button_id} in {update_type}")
            return False

        button_id = aux_data.get("button_id") or aux_data.get(
            "callback_data") or ""
        result = button_id == self.button_id
        logger.info(
            f"ButtonFilter check for button_id={
                self.button_id} in {update_type}: {result}, aux_data={aux_data}")
        return result


class UpdateTypeFilter(Filter):
    def __init__(self, update_types: Union[str, List[str]]):
        self.update_types = [update_types] if isinstance(
            update_types, str) else update_types

    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        result = (isinstance(update, Update) and update.type in self.update_types) or (
            isinstance(update, InlineMessage) and "InlineMessage" in self.update_types)
        logger.info(
            f"UpdateTypeFilter check for types={
                self.update_types}, update={
                type(update).__name__}: {result}")
        return result


class BotClient:
    def __init__(
            self,
            token: str,
            state_file: str = "bot_state.json",
            rate_limit: float = 0.5,
            use_webhook: bool = False):
        self.token = token
        self.base_url = f"https://botapi.rubika.ir/v3/{token}/"
        self.handlers: Dict[str,
                            List[Tuple[Tuple[Filter, ...], Callable]]] = {}
        self.session = None
        self.running = False
        self.next_offset_id = None
        self.processed_messages = deque(maxlen=10000)
        self.state_file = state_file
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.use_webhook = use_webhook
        if not use_webhook and os.path.exists(state_file):
            self._load_state()
        logger.info("Rubika client initialized, use_webhook=%s", use_webhook)

    def _load_state(self):
        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)
                self.next_offset_id = state.get("next_offset_id")
                self.processed_messages = deque(
                    state.get("processed_messages", []),
                    maxlen=10000)
                logger.info(
                    f"Loaded state: next_offset_id={self.next_offset_id}")
        except Exception as e:
            logger.error(f"Failed to load state: {str(e)}")

    def _save_state(self):
        if self.use_webhook:
            logger.debug("Skipping state save in webhook mode")
            return
        try:
            state = {
                "next_offset_id": self.next_offset_id,
                "processed_messages": list(self.processed_messages)
            }
            with open(self.state_file, "w") as f:
                json.dump(state, f)
            logger.debug("State saved")
        except Exception as e:
            logger.error(f"Failed to save state: {str(e)}")

    async def _rate_limit_delay(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            await asyncio.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    async def start(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        self.running = True
        logger.info("Rubika client started")

    async def stop(self):
        if self.session and not self.session.closed:
            await self.session.close()
        self.running = False
        if not self.use_webhook:
            self._save_state()
        logger.info("Rubika client stopped")

    async def _make_request(self, method: str, data: Dict) -> Dict:
        await self._rate_limit_delay()
        url = f"{self.base_url}{method}"
        try:
            async with self.session.post(url, json=data) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(
                        f"Request failed: {method} status={
                            response.status} body={text}")
                    raise aiohttp.ClientResponseError(
                        response.request_info, response.history,
                        status=response.status, message=text)
                result = await response.json()
                logger.debug(f"API response for {method}: {result}")
                return result
        except Exception as e:
            logger.error(f"Error in _make_request for {method}: {str(e)}")
            return {"status": "ERROR", "error": str(e)}

    async def get_me(self) -> Dict:
        response = await self._make_request("getMe", {})
        if response.get("status") != "OK":
            logger.error(f"API error in getMe: {response}")
            return {}
        return response.get("data", {})

    async def send_message(
        self,
        chat_id: str,
        text: str,
        chat_keypad: Optional[Keypad] = None,
        inline_keypad: Optional[Keypad] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[str] = None,
        chat_keypad_type: ChatKeypadTypeEnum = ChatKeypadTypeEnum.NONE
    ) -> Dict:
        data = {
            "chat_id": chat_id,
            "text": text,
            "disable_notification": disable_notification,
            "chat_keypad_type": chat_keypad_type.value
        }
        if chat_keypad:
            data["chat_keypad"] = dataclasses.asdict(chat_keypad)
        if inline_keypad:
            data["inline_keypad"] = dataclasses.asdict(inline_keypad)
        if reply_to_message_id:
            data["reply_to_message_id"] = str(reply_to_message_id)
        try:
            response = await self._make_request("sendMessage", data)
            if response.get(
                    "status") == "OK" and "data" in response and "message_id" in response["data"]:
                self.processed_messages.append(
                    str(response["data"]["message_id"]))
                if not self.use_webhook:
                    self._save_state()
                logger.info(
                    f"Message sent successfully to chat_id={chat_id}, message_id={
                        response['data']['message_id']}")
            else:
                logger.error(f"Failed to send message: {response}")
            return response
        except Exception as e:
            logger.error(
                f"Error sending message to chat_id={chat_id}: {str(e)}")
            return {"status": "ERROR", "error": str(e)}

    async def send_message_with_buttons(
        self,
        chat_id: str,
        text: str,
        buttons: List[List[Dict]] = None
    ) -> Dict:
        inline_keypad = None
        if buttons:
            inline_keypad = Keypad(
                rows=[
                    KeypadRow(
                        buttons=[
                            Button(
                                id=btn["id"],
                                type=ButtonTypeEnum.SIMPLE,
                                button_text=btn["text"])
                            for btn in row]) for row in buttons])
        return await self.send_message(chat_id, text, inline_keypad=inline_keypad)

    async def send_poll(
            self,
            chat_id: str,
            question: str,
            options: List[str]) -> Dict:
        data = {
            "chat_id": chat_id,
            "question": question,
            "options": options
        }
        response = await self._make_request("sendPoll", data)
        if response.get(
                "status") == "OK" and "data" in response and "message_id" in response["data"]:
            self.processed_messages.append(str(response["data"]["message_id"]))
            if not self.use_webhook:
                self._save_state()
        return response

    async def send_location(
        self,
        chat_id: str,
        latitude: str,
        longitude: str,
        chat_keypad: Optional[Keypad] = None,
        inline_keypad: Optional[Keypad] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[str] = None,
        chat_keypad_type: ChatKeypadTypeEnum = ChatKeypadTypeEnum.NONE
    ) -> Dict:
        data = {
            "chat_id": chat_id,
            "latitude": str(latitude),
            "longitude": str(longitude),
            "disable_notification": disable_notification,
            "chat_keypad_type": chat_keypad_type.value
        }
        if chat_keypad:
            data["chat_keypad"] = dataclasses.asdict(chat_keypad)
        if inline_keypad:
            data["inline_keypad"] = dataclasses.asdict(inline_keypad)
        if reply_to_message_id:
            data["reply_to_message_id"] = str(reply_to_message_id)
        response = await self._make_request("sendLocation", data)
        if response.get(
                "status") == "OK" and "data" in response and "message_id" in response["data"]:
            self.processed_messages.append(str(response["data"]["message_id"]))
            if not self.use_webhook:
                self._save_state()
        return response

    async def send_contact(
        self,
        chat_id: str,
        first_name: str,
        last_name: str,
        phone_number: str,
        chat_keypad: Optional[Keypad] = None,
        inline_keypad: Optional[Keypad] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[str] = None,
        chat_keypad_type: ChatKeypadTypeEnum = ChatKeypadTypeEnum.NONE
    ) -> Dict:
        data = {
            "chat_id": chat_id,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            "disable_notification": disable_notification,
            "chat_keypad_type": chat_keypad_type.value
        }
        if chat_keypad:
            data["chat_keypad"] = dataclasses.asdict(chat_keypad)
        if inline_keypad:
            data["inline_keypad"] = dataclasses.asdict(inline_keypad)
        if reply_to_message_id:
            data["reply_to_message_id"] = str(reply_to_message_id)
        response = await self._make_request("sendContact", data)
        if response.get(
                "status") == "OK" and "data" in response and "message_id" in response["data"]:
            self.processed_messages.append(str(response["data"]["message_id"]))
            if not self.use_webhook:
                self._save_state()
        return response

    async def get_chat(self, chat_id: str) -> Dict:
        response = await self._make_request("getChat", {"chat_id": chat_id})
        if response.get("status") != "OK":
            logger.error(f"API error in getChat: {response}")
            return {}
        return response.get("data", {})

    async def get_updates(self,
                          limit: int = 100,
                          offset_id: str = "") -> List[Union[Update,
                                                             InlineMessage]]:
        data = {"limit": limit}
        if offset_id or self.next_offset_id:
            data["offset_id"] = self.next_offset_id if not offset_id else offset_id
        updates = []
        try:
            response = await self._make_request("getUpdates", data)
            for item in response.get("data", {}).get("updates", []):
                update = self._parse_update(item)
                if update:
                    updates.append(update)
            self.next_offset_id = response.get(
                "data", {}).get("next_offset_id")
            if not self.use_webhook:
                self._save_state()
        except Exception as e:
            logger.exception(f"Failed to get updates: {str(e)}")
        return updates

    async def forward_message(
        self,
        from_chat_id: str,
        message_id: str,
        to_chat_id: str,
        disable_notification: bool = False
    ) -> Dict:
        data = {
            "from_chat_id": from_chat_id,
            "message_id": str(message_id),
            "to_chat_id": to_chat_id,
            "disable_notification": disable_notification
        }
        response = await self._make_request("forwardMessage", data)
        if response.get(
                "status") == "OK" and "data" in response and "new_message_id" in response["data"]:
            self.processed_messages.append(
                str(response["data"]["new_message_id"]))
            if not self.use_webhook:
                self._save_state()
        return response

    async def edit_message_text(
            self,
            chat_id: str,
            message_id: str,
            text: str) -> Dict:
        data = {
            "chat_id": chat_id,
            "message_id": str(message_id),
            "text": text
        }
        return await self._make_request("editMessageText", data)

    async def edit_message_keypad(
        self,
        chat_id: str,
        message_id: str,
        inline_keypad: Keypad
    ) -> Dict:
        data = {
            "chat_id": chat_id,
            "message_id": str(message_id),
            "inline_keypad": dataclasses.asdict(inline_keypad)
        }
        return await self._make_request("editMessageKeypad", data)

    async def delete_message(self, chat_id: str, message_id: str) -> Dict:
        data = {
            "chat_id": chat_id,
            "message_id": str(message_id)
        }
        return await self._make_request("deleteMessage", data)

    async def set_commands(self, bot_commands: List[Dict]) -> Dict:
        return await self._make_request("setCommands", {"bot_commands": bot_commands})

    async def update_bot_endpoints(self, url: str, type: str) -> Dict:
        response = await self._make_request("updateBotEndpoints", {"url": url, "type": type})
        logger.info(f"updateBotEndpoints response for {type}: {response}")
        return response

    async def edit_chat_keypad(
        self,
        chat_id: str,
        chat_keypad_type: ChatKeypadTypeEnum,
        chat_keypad: Optional[Keypad] = None
    ) -> Dict:
        data = {
            "chat_id": chat_id,
            "chat_keypad_type": chat_keypad_type.value
        }
        if chat_keypad:
            data["chat_keypad"] = dataclasses.asdict(chat_keypad)
        return await self._make_request("editChatKeypad", data)

    def on_update(self, *filters: Filter) -> Callable:
        def decorator(handler: Callable) -> Callable:
            filter_key = str(uuid.uuid4())
            if filter_key not in self.handlers:
                self.handlers[filter_key] = []
            self.handlers[filter_key].append((filters, handler))
            logger.info(
                f"Registered handler {
                    handler.__name__} with filters: {filters}")
            return handler
        return decorator

    def _parse_update(
            self, item: Dict) -> Optional[Union[Update, InlineMessage]]:
        update_type = item.get("type")
        if not update_type:
            logger.debug(f"Skipping update with no type: {item}")
            return None

        chat_id = item.get("chat_id", "")
        if update_type == UpdateTypeEnum.REMOVED_MESSAGE:
            return Update(
                client=self,
                type=UpdateTypeEnum.REMOVED_MESSAGE,
                chat_id=chat_id,
                removed_message_id=str(item.get("removed_message_id", ""))
            )
        elif update_type in [UpdateTypeEnum.NEW_MESSAGE, UpdateTypeEnum.UPDATED_MESSAGE]:
            msg_key = "new_message" if update_type == UpdateTypeEnum.NEW_MESSAGE else "updated_message"
            msg_data = item.get(msg_key)
            if not msg_data:
                logger.debug(
                    f"Skipping {msg_key} with no message data: {item}")
                return None

            msg_data["message_id"] = str(msg_data.get("message_id", ""))
            try:
                message_obj = Message(**msg_data)
                return Update(
                    client=self, type=update_type, chat_id=chat_id,
                    new_message=message_obj
                    if update_type == UpdateTypeEnum.NEW_MESSAGE else None,
                    updated_message=message_obj
                    if update_type == UpdateTypeEnum.UPDATED_MESSAGE else None)
            except Exception as e:
                logger.error(
                    f"Failed to parse message: {msg_data}, error: {str(e)}")
                return None
        elif update_type == "InlineMessage":
            try:
                inline_msg = InlineMessage(
                    sender_id=item.get("sender_id", ""),
                    text=item.get("text", ""),
                    message_id=str(item.get("message_id", "")),
                    chat_id=chat_id,
                    file=item.get("file"),
                    location=item.get("location"),
                    aux_data=item.get("aux_data")
                )
                logger.info(f"Parsed InlineMessage: {inline_msg}")
                return inline_msg
            except Exception as e:
                logger.error(
                    f"Failed to parse InlineMessage: {item}, error: {str(e)}")
                return None
        else:
            logger.debug(f"Unhandled update type: {update_type}, data: {item}")
            return None

    async def process_update(self, update: Union[Update, InlineMessage]):
        update_type = "InlineMessage" if isinstance(
            update, InlineMessage) else update.type
        message_id = self._extract_message_id(update)

        # Skip processed messages check for InlineMessage to avoid issues with
        # repeated message_id
        if isinstance(
                update,
                Update) and message_id and message_id in self.processed_messages:
            logger.debug(
                f"Skipping processed update ({update_type}): {message_id}")
            return

        if message_id and isinstance(update, Update):
            self.processed_messages.append(message_id)
            if not self.use_webhook:
                self._save_state()

        handled = False
        for filter_key, handler_list in self.handlers.items():
            for filters, handler in handler_list:
                if await self._filters_pass(update, filters):
                    try:
                        logger.info(
                            f"Executing handler {
                                handler.__name__} for update {update_type}")
                        await handler(self, update)
                        handled = True
                    except Exception as e:
                        logger.exception(
                            f"Error in handler {handler.__name__}: {str(e)}")
                else:
                    pass

    def _extract_message_id(
            self, update: Union[Update, InlineMessage]) -> Optional[str]:
        if isinstance(update, InlineMessage):
            return update.message_id
        if isinstance(update, Update):
            if update.type == UpdateTypeEnum.REMOVED_MESSAGE:
                return update.removed_message_id
            if update.new_message:
                return update.new_message.message_id
            if update.updated_message:
                return update.updated_message.message_id
        return None

    async def _filters_pass(
            self, update: Union[Update, InlineMessage],
            filters: Tuple[Filter, ...]) -> bool:
        update_type = "InlineMessage" if isinstance(
            update, InlineMessage) else update.type
        for f in filters:
            result = await f.check(update)
            if not result:
                return False
        return True

    async def handle_webhook(self, request: web.Request) -> web.Response:
        if request.method != "POST":
            logger.error(f"Invalid method: {request.method}")
            return web.Response(status=405, text="Method Not Allowed")

        try:
            data = await request.json()
            logger.debug(
                f"Webhook payload for {
                    request.path}: {
                    json.dumps(
                        data,
                        ensure_ascii=False)}")
            updates = []

            # Handle inline_message
            if "inline_message" in data:
                try:
                    inline_msg = InlineMessage(
                        sender_id=data["inline_message"].get(
                            "sender_id", ""),
                        text=data["inline_message"].get("text", ""),
                        message_id=str(
                            data["inline_message"].get("message_id", "")),
                        chat_id=data["inline_message"].get("chat_id", ""),
                        file=data["inline_message"].get("file"),
                        location=data["inline_message"].get("location"),
                        aux_data=data["inline_message"].get("aux_data"))
                    updates.append(inline_msg)
                except Exception as e:
                    logger.error(f"Failed to parse InlineMessage: {str(e)}")

            # Handle updates
            elif "update" in data:
                update = self._parse_update(data["update"])
                if update:
                    updates.append(update)

            for update in updates:
                asyncio.create_task(self.process_update(update))

            return web.json_response({"status": "OK"})
        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook request")
            return web.json_response(
                {"status": "ERROR", "error": "Invalid JSON"},
                status=400)
        except Exception as e:
            logger.error(f"Webhook error for {request.path}: {str(e)}")
            return web.json_response(
                {"status": "ERROR", "error": str(e)},
                status=500)

    async def run(
            self,
            webhook_url: Optional[str] = None,
            path: Optional[str] = '/webhook',
            host: str = "0.0.0.0",
            port: int = 8080):
        self.use_webhook = bool(webhook_url)
        await self.start()
        if self.use_webhook:
            app = web.Application()
            webhook_base = path.rstrip('/')
            app.router.add_post(f"{webhook_base}", self.handle_webhook)
            app.router.add_post(
                f"{webhook_base}/receiveUpdate",
                self.handle_webhook)
            app.router.add_post(
                f"{webhook_base}/receiveInlineMessage",
                self.handle_webhook)

            webhook_url = f"{webhook_url.rstrip('/')}{webhook_base}"
            for endpoint_type in ["ReceiveUpdate", "ReceiveInlineMessage"]:
                response = await self.update_bot_endpoints(webhook_url, endpoint_type)

            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host, port)
            await site.start()
            try:
                while self.running:
                    await asyncio.sleep(1)
            finally:
                await runner.cleanup()
        else:
            while self.running:
                try:
                    updates = await self.get_updates(limit=100)
                    for update in updates:
                        asyncio.create_task(self.process_update(update))
                    await asyncio.sleep(1)
                except Exception as error:
                    logger.error(f"Polling error: {str(error)}")
                    await asyncio.sleep(5)
