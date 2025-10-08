import time
import json
import uuid
import websocket
from threading import Thread
from typing import Optional
from dataclasses import dataclass, asdict

from ..lib.util import helpers

class SocketHandler:
    def __init__(self, client, socket_trace=False, debug=False, auto_run=False):
        self.socket_url = "wss://ws1.aminoapps.com"
        self.client = client
        self.debug = debug
        self.active = False
        self.headers = None
        self.socket = None
        self.socket_thread = None
        self.reconnectTime = 180
        self.reconnect_thread = None

        websocket.enableTrace(socket_trace)

        if auto_run and self.client.sid:
            self.run_amino_socket()

    def reconnect_handler(self):
        while True:
            time.sleep(self.reconnectTime)
            if self.active:
                if self.debug:
                    print(f"[socket][reconnect_handler] Reconnecting Socket")
                self.close()
                self.run_amino_socket()

    def handle_message(self, ws, data):
        self.client.handle_socket_message(data)

    def send(self, data):
        if self.debug:
            print(f"[socket][send] Sending Data : {data}")
        if not self.socket_thread:
            self.run_amino_socket()
            time.sleep(5)
        self.socket.send(data)

    def run_amino_socket(self):
        try:
            if self.debug:
                print(f"[socket][start] Starting Socket")

            if self.client.sid is None:
                return

            final = f"{self.client.device_id}|{int(time.time() * 1000)}"

            self.headers = {
                "NDCDEVICEID": self.client.device_id,
                "NDCAUTH": f"sid={self.client.sid}",
                "NDC-MSG-SIG": helpers.signature(final)
            }

            self.socket = websocket.WebSocketApp(
                f"{self.socket_url}/?signbody={final.replace('|', '%7C')}",
                on_message=self.handle_message,
                header=self.headers
            )

            self.active = True
            self.socket_thread = Thread(target=self.socket.run_forever)
            self.socket_thread.start()

            if self.reconnect_thread is None:
                self.reconnect_thread = Thread(target=self.reconnect_handler)
                self.reconnect_thread.start()

            if self.debug:
                print(f"[socket][start] Socket Started")
        except Exception as e:
            print(e)

    def close(self):
        if self.debug:
            print(f"[socket][close] Closing Socket")
        self.active = False
        try:
            self.socket.close()
        except Exception as closeError:
            if self.debug:
                print(f"[socket][close] Error while closing Socket : {closeError}")



@dataclass
class BasePayload:
    ndcId: int
    threadId: str
    joinRole: int = 1
    channelType: Optional[int] = None
    t: int = 112

    def to_dict(self):
        data = {"o": asdict(self), "t": self.t}
        if self.channelType is None:
            data["o"].pop("channelType")
        return data



# ======================
# SocketActions
# ======================
class SocketActions:
    def __init__(self, client):
        self.client = client
        self.active_live_chats: list[str] = []
        self.stop_loop: bool = False

    def _send_payload(self, payload: BasePayload):
        data = payload.to_dict()
        data["o"]["id"] = str(uuid.uuid4())
        self.client.send(json.dumps(data))

    def join_voice_chat(self, comId: str, chatId: str, joinRole: int = 1):
        payload = BasePayload(ndcId=int(comId), threadId=chatId, joinRole=joinRole, t=112)
        self._send_payload(payload)

    def join_video_chat(self, comId: str, chatId: str, joinRole: int = 1):
        payload = BasePayload(ndcId=int(comId), threadId=chatId, joinRole=joinRole, channelType=5, t=108)
        self._send_payload(payload)

    def join_video_chat_as_viewer(self, comId: str, chatId: str):
        payload = BasePayload(ndcId=int(comId), threadId=chatId, joinRole=2, t=112)
        self._send_payload(payload)

    def start_vc(self, comId: str, chatId: str, joinRole: int = 1):
        self.join_voice_chat(comId, chatId, joinRole)
        payload = BasePayload(ndcId=int(comId), threadId=chatId, joinRole=joinRole, channelType=1, t=108)
        self._send_payload(payload)
        self.active_live_chats.append(chatId)
        Thread(target=lambda: self._run_vc_loop(comId, chatId, joinRole), daemon=True).start()

    def _run_vc_loop(self, comId: str, chatId: str, joinRole: int):
        while chatId in self.active_live_chats and not self.stop_loop:
            self.join_voice_chat(comId, chatId, joinRole)
            time.sleep(60)

    def end_vc(self, comId: str, chatId: str, joinRole: int = 2):
        if chatId in self.active_live_chats:
            self.active_live_chats.remove(chatId)
        self.stop_loop = True
        self.join_voice_chat(comId, chatId, joinRole)

    def leave_from_live_chat(self, chatId: str):
        if chatId in self.active_live_chats:
            self.active_live_chats.remove(chatId)
