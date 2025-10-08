# If you try to steal something I will fuck you


import json
from ..lib.util import objects


class Context:
    def __init__(self, data: objects.Event):
        self.data: objects.Event = data
        self.message = self.data.message
        self.author = self.message.author

    @property
    def userId(self):
        return self.author.userId

    @property
    def comId(self):
        return self.data.json["ndcId"]

    @property
    def chatId(self):
        return self.message.chatId

    @property
    def messageId(self):
        return self.message.messageId

    @property
    def content(self):
        return self.message.content

    @property
    def stickerId(self):
    	return self.message.sticker.stickerId

    def reply(self, message: str):
        from ..sub_client import SubClient
        sub = SubClient(comId=self.comId)
        return sub.send_message(chatId=self.chatId, message=message, replyTo=self.messageId)

    def send_message(self, message: str):
        from ..sub_client import SubClient
        sub = SubClient(comId=self.comId)
        return sub.send_message(chatId=self.chatId, message=message)


class Callbacks:
    def __init__(self, client, debug=False):
        self.client = client
        self.debug = debug
        self.handlers = {}
        self.methods = {
            304: self._resolve_chat_action_start,
            306: self._resolve_chat_action_end,
            1000: self._resolve_chat_message
        }
        self.chat_methods = {
            "0:0": "on_text_message",
            "0:100": "on_image_message",
            "0:103": "on_youtube_message",
            "1:0": "on_strike_message",
            "2:110": "on_voice_message",
            "3:113": "on_sticker_message",
            "52:0": "on_voice_chat_not_answered",
            "53:0": "on_voice_chat_not_cancelled",
            "54:0": "on_voice_chat_not_declined",
            "55:0": "on_video_chat_not_answered",
            "56:0": "on_video_chat_not_cancelled",
            "57:0": "on_video_chat_not_declined",
            "58:0": "on_avatar_chat_not_answered",
            "59:0": "on_avatar_chat_not_cancelled",
            "60:0": "on_avatar_chat_not_declined",
            "100:0": "on_delete_message",
            "101:0": "on_group_member_join",
            "102:0": "on_group_member_leave",
            "103:0": "on_chat_invite",
            "104:0": "on_chat_background_changed",
            "105:0": "on_chat_title_changed",
            "106:0": "on_chat_icon_changed",
            "107:0": "on_voice_chat_start",
            "108:0": "on_video_chat_start",
            "109:0": "on_avatar_chat_start",
            "110:0": "on_voice_chat_end",
            "111:0": "on_video_chat_end",
            "112:0": "on_avatar_chat_end",
            "113:0": "on_chat_content_changed",
            "114:0": "on_screen_room_start",
            "115:0": "on_screen_room_end",
            "116:0": "on_chat_host_transfered",
            "117:0": "on_text_message_force_removed",
            "118:0": "on_chat_removed_message",
            "119:0": "on_text_message_removed_by_admin",
            "120:0": "on_chat_tip",
            "121:0": "on_chat_pin_announcement",
            "122:0": "on_voice_chat_permission_open_to_everyone",
            "123:0": "on_voice_chat_permission_invited_and_requested",
            "124:0": "on_voice_chat_permission_invite_only",
            "125:0": "on_chat_view_only_enabled",
            "126:0": "on_chat_view_only_disabled",
            "127:0": "on_chat_unpin_announcement",
            "128:0": "on_chat_tipping_enabled",
            "129:0": "on_chat_tipping_disabled",
            "65281:0": "on_timestamp_message",
            "65282:0": "on_welcome_message",
            "65283:0": "on_invite_message",
        }

        self.client.handle_socket_message = self.resolve

    def _log(self, msg):
        if self.debug:
            print(f"[callbacks] {msg}")

    def auto_register(self, scope, prefix="on_"):
        for name, func in scope.items():
            if callable(func) and name.startswith(prefix):
                self.handlers[name] = [func]
                self._log(f"Registered event: {name}")

    def _dispatch(self, event_name, payload):
        event_data = objects.Event(payload).Event
        ctx = Context(event_data)
        for handler in self.handlers.get(event_name, []):
            try:
                handler(ctx)
            except Exception as e:
                self._log(f"Handler {event_name} failed: {e}")

    def _resolve_chat_message(self, data):
        key = f"{data['o']['chatMessage']['type']}:{data['o']['chatMessage'].get('mediaType',0)}"
        event_name = self.chat_methods.get(key, "default")
        self._dispatch(event_name, data["o"])

    def _resolve_chat_action_start(self, data):
        self._dispatch("on_user_typing_start", data["o"])

    def _resolve_chat_action_end(self, data):
        self._dispatch("on_user_typing_end", data["o"])

    def resolve(self, raw_data):
        try:
            data = json.loads(raw_data)
            resolver = self.methods.get(data["t"], self.default)
            resolver(data)
        except Exception as e:
            self._log(f"Error parsing data: {e}")

    def default(self, data):
        self._dispatch("default", data)