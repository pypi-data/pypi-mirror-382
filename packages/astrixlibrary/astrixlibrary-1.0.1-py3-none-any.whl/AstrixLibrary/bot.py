import requests
import socketio
import uuid
import threading
import time
import inspect
class Context:
    def __init__(self, bot, chat_id, message):
        self.bot = bot
        self.chat_id = chat_id
        self.message = message

    def send(self, text: str):
        self.bot.send_message(self.chat_id, text)
    def start_typing(self):
        try:
            self.bot.socket.emit("typing", self.chat_id)
        except Exception as e:
            print(f"[AstrixRU] Error start_typing: {e}")

    def stop_typing(self):
        try:
            self.bot.socket.emit("stop_typing", self.chat_id)
        except Exception as e:
            print(f"[AstrixRU] Error stop_typing: {e}")
    def delete_message(self, message_timestamp: str):
        self.bot.delete_message(self.chat_id, message_timestamp)
    def react(self, message_timestamp: str, emoji: str):
        self.bot.react_to_message(self.chat_id, message_timestamp, emoji)

    def pin(self, message_timestamp: str):
        self.bot.pin_message(self.chat_id, message_timestamp)

    def unpin(self, message_timestamp: str):
        self.bot.unpin_message(self.chat_id, message_timestamp)

    def edit(self, message_timestamp: str, new_text: str):
        self.bot.edit_message(self.chat_id, message_timestamp, new_text)
class AstrixBot:
    def __init__(self, token: str, api_url: str = "https://astrixru.online"):
        self.api_url = api_url.rstrip("/")
        self.token = token
        self.session_token = None
        self.bot_nickname = None
        self.socket = socketio.Client()
        self.joined_chats = set()
        self.commands = {}
        self.socket.on("connect", self._on_connect)
        self.socket.on("disconnect", self._on_disconnect)
        self.socket.on("connect_error", self._on_connect_error)
        self.socket.on("new_message", self._on_new_message)
        self.socket.on("wallet_updated", self._on_wallet_updated)
    def login(self):
        print("[BOT] Starting...")
        res = requests.post(
            f"{self.api_url}/api/bot/login",
            json={"token": self.token},
            headers={"Content-Type": "application/json"},
        )
        if not res.ok:
            raise Exception(f"[BOT] Auth error: {res.text}")

        data = res.json()
        self.session_token = data.get("sessionToken")
        self.bot_nickname = data.get("bot", {}).get("name")
        if not self.session_token:
            raise Exception("[BOT] Failed to get sessionToken from API")

        print("[BOT] Authorization successful")
        print(f"[BOT] Bot nickname: {self.bot_nickname}")
    def connect(self):
        print("[BOT] Connecting to Socket.IO...")
        self.socket.connect(
            self.api_url,
            transports=["websocket"],
            auth={
                "nickname": self.bot_nickname,
                "sessionToken": self.session_token,
            },
        )
        threading.Thread(target=self._friend_checker_loop, daemon=True).start()

    def run_forever(self):
        print("[BOT] Running... Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    def _on_connect(self):
        print("[BOT] Connected to server")

    def _on_disconnect(self):
        print("[BOT] Disconnected from server")

    def _on_connect_error(self, err):
        print(f"[BOT] Connection error: {err}")
    def newCommand(self, command_name):
        def decorator(func):
            self.commands[command_name] = func
            return func

        return decorator
    def _on_new_message(self, message):
        if not message or "chatId" not in message or "text" not in message:
            return
        if message.get("sender") == self.bot_nickname:
            return
        chat_id = message["chatId"]
        text = message["text"].strip()
        parts = text.split()
        if not parts:
            return
        cmd = parts[0]
        args = parts[1:]
        if chat_id not in self.joined_chats:
            self.join_chat(chat_id)
        if cmd in self.commands:
            ctx = Context(self, chat_id, message)
            try:
                func = self.commands[cmd]
                sig = inspect.signature(func)
                if any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in sig.parameters.values()):
                    func(ctx, *args)
                else:
                    func(ctx, *args[: len(sig.parameters) - 1])
            except Exception as e:
                print(f"Error: {e}")
    def join_chat(self, chat_id):
        self.socket.emit("join_chat", chat_id)
        self.joined_chats.add(chat_id)
        print(f"[BOT] Joined chat: {chat_id}")

    def send_message(self, chat_id, text):
        self.socket.emit(
            "send_message",
            {"chatId": chat_id, "id": str(uuid.uuid4()), "text": text},
            callback=self._on_send_callback,
        )

    def _on_send_callback(self, callback):
        if not callback or not callback.get("success"):
            print("[AstrixRU] Error sending message:", callback.get("error"))

    def get_conversations(self):
        if not self.session_token:
            print("[BOT] Error: Bot is not logged.")
            return None
    
        url = f"{self.api_url}/api/bot/conversations"
        try:
            response = requests.get(url, headers={"sessiontoken": self.session_token})
            if response.status_code == 401:
                print("[BOT] Error: Authorization required (bot not recognized)")
                return None
            response.raise_for_status()
            data = response.json()
            if data.get("success"):
                return data["conversations"]
            else:
                print("[AstrixRU] Error retrieving chats:", data)
                return None
        except Exception as e:
            print(f"[AstrixRU] Request error /api/conversations: {e}")
            return None
    def find_user(self, nickname: str):
        url = f"{self.api_url}/api/profile/{nickname}"
        try:
            response = requests.get(url, headers={"Content-Type": "application/json"})
            if not response.ok:
                print(f"[AstrixRU] Error while searching user {nickname}: {response.status_code}")
                return None
    
            data = response.json()
            if not data.get("success"):
                return None
    
            profile = data.get("profile")
            return profile
    
        except Exception as e:
            print(f"[AstrixRU] Error requesting profile {nickname}: {e}")
            return None
    def get_music(self, page: int = 1, query: str = None):
        if not self.session_token:
            print("[BOT] Error: Bot is not logged.")
            return None
    
        url = f"{self.api_url}/api/bot/music/list?page={page}"
        if query:
            url += f"&query={query}"
    
        try:
            headers = {
                "sessiontoken": self.session_token,
                "Content-Type": "application/json"
            }
            response = requests.get(url, headers=headers)
    
            if response.status_code == 401:
                print("[BOT] ❌ Error: Authorization required (bot not recognized)")
                return None
    
            response.raise_for_status()
            data = response.json()
    
            if not data.get("success"):
                print("[AstrixRU] ❌ Error retrieving music:", data)
                return None
    
            tracks = data.get("tracks", [])
            has_next = data.get("hasNextPage", False)
    
            music_list = []
            for track in tracks:
                music_list.append({
                    "id": track.get("id"),
                    "title": track.get("title"),
                    "artist": track.get("artist"),
                    "url": track.get("url"),
                    "uploader": track.get("uploader"),
                    "uploadDate": track.get("uploadDate")
                })
    
            return {
                "music": music_list,
                "has_next": has_next
            }
    
        except Exception as e:
            print(f"[AstrixRU] ❌ Error fetching music list: {e}")
            return None
    def delete_message(self, chat_id: str, message_timestamp: str):
        try:
            self.socket.emit(
                "delete_message",
                {"chatId": chat_id, "messageTimestamp": message_timestamp},
                callback=self._on_delete_callback,
            )
        except Exception as e:
            print(f"[AstrixRU] Error deleting message: {e}")

    def _on_delete_callback(self, callback):
        if not callback or not callback.get("success"):
            print("[AstrixRU] ❌ Error deleting message:", callback.get("error"))

    def react_to_message(self, chat_id: str, message_timestamp: str, emoji: str):
        try:
            self.socket.emit(
                "react_to_message",
                {
                    "chatId": chat_id,
                    "messageTimestamp": message_timestamp,
                    "emoji": emoji,
                },
                callback=self._on_react_callback,
            )
        except Exception as e:
            print(f"[AstrixRU] Error reacting to message: {e}")

    def _on_react_callback(self, callback):
        if not callback or not callback.get("success"):
            print("[AstrixRU] ❌ Error reacting to message:", callback.get("error"))

    def pin_message(self, chat_id: str, message_timestamp: str):
        try:
            self.socket.emit(
                "pin_message",
                {"chatId": chat_id, "messageTimestamp": message_timestamp},
                callback=self._on_pin_callback,
            )
        except Exception as e:
            print(f"[AstrixRU] Error pinning message: {e}")

    def unpin_message(self, chat_id: str, message_timestamp: str):
        try:
            self.socket.emit(
                "unpin_message",
                {"chatId": chat_id, "messageTimestamp": message_timestamp},
                callback=self._on_pin_callback,
            )
        except Exception as e:
            print(f"[AstrixRU] Error unpinning message: {e}")

    def _on_pin_callback(self, callback):
        if not callback or not callback.get("success"):
            print("[BOT] ❌ Error pinning/unpinning message:", callback.get("error"))
        else:
            print("[BOT] ✅ Pin/unpin successful")

    def edit_message(self, chat_id: str, message_timestamp: str, new_text: str):
        try:
            self.socket.emit(
                "edit_message",
                {
                    "chatId": chat_id,
                    "messageTimestamp": message_timestamp,
                    "newText": new_text,
                },
                callback=self._on_edit_callback,
            )
        except Exception as e:
            print(f"[AstrixRU] Error editing message: {e}")

    def _on_edit_callback(self, callback):
        if not callback or not callback.get("success"):
            print("[AstrixRU] ❌ Error editing message:", callback.get("error"))

    def _on_wallet_updated(self, data):
        new_balance = data.get('newBalance')
        message = data.get('message')
        sender_info = data.get('senderInfo', {})
        amount = data.get('amount')
        if hasattr(self, 'on_wallet_updated') and callable(self.on_wallet_updated):
            try:
                self.on_wallet_updated(
                    new_balance=new_balance,
                    message=message,
                    sender_info=sender_info,
                    amount=amount
                )
            except Exception as e:
                print(f"[AstrixRU] Error in custom on_wallet_updated handler: {e}")

    def _friend_checker_loop(self):
        while True:
            try:
                res = requests.get(f"{self.api_url}/api/friends/list")
                if not res.ok:
                    continue
                data = res.json()
                for req in data.get("requestsReceived", []):
                    requests.post(
                        f"{self.api_url}/api/friends/accept-request",
                        json={"senderNickname": req["nickname"]},
                        headers={"Content-Type": "application/json"},
                    )
            except Exception as e:
                print("[AstrixRU] Error checking friend requests:", e)
            time.sleep(15)