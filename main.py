# main.py
import os

os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

import time
import threading
import functools

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.clock import Clock

from ui.screens.home_screen import HomeScreen
from ui.screens.chat_screen import ChatScreen
from network.discovery import PeerDiscovery
from network.server import ChatServer
from network.client import ChatClient
from config.settings import DEFAULT_DEVICE_NAME
from utils.arabic_support import register_arabic_font

Window.size = (360, 640)


class AirChatApp(MDApp):

    def build(self):
        # تسجيل الخط العربي أولاً، قبل إنشاء أي واجهة تستخدم نصوصاً عربية
        register_arabic_font()

        self.device_name = DEFAULT_DEVICE_NAME
        self.chat_histories = {}  # {peer_ip أو "GROUP": [msg, msg, ...]}

        self.sm = ScreenManager(transition=NoTransition())

        self.home_screen = HomeScreen(
            name="home",
            on_user_select_callback=self.open_chat,
        )
        self.chat_screen = ChatScreen(
            name="chat",
            on_back_callback=self.go_to_home,
            on_send_callback=self.send_message,
        )

        self.sm.add_widget(self.home_screen)
        self.sm.add_widget(self.chat_screen)

        # --- تهيئة خدمات الشبكة ---
        self.discovery = PeerDiscovery(
            device_name=self.device_name,
            on_peers_updated_callback=self._on_peers_updated,
        )
        self.server = ChatServer(
            on_message_received_callback=self._on_message_received,
        )

        return self.sm

    def on_start(self):
        """بدء خدمات الشبكة بعد جاهزية الواجهة."""
        self.discovery.start()
        self.server.start()

    def on_stop(self):
        """إيقاف خدمات الشبكة بشكل نظيف عند إغلاق التطبيق."""
        self.discovery.stop()
        self.server.stop()

    # ---------- التنقل بين الشاشات ----------
    def open_chat(self, peer_data):
        key = "GROUP" if peer_data.get("is_group") else peer_data.get("ip")
        history = self.chat_histories.get(key, [])
        self.chat_screen.set_active_chat(peer_data, history)
        self.sm.current = "chat"

    def go_to_home(self):
        self.sm.current = "home"

    # ---------- استقبال تحديثات قائمة الأجهزة (من خيط الاكتشاف) ----------
    def _on_peers_updated(self, peers_snapshot: dict):
        # ننفذ التحديث على الخيط الرئيسي دائماً لأنه يلمس واجهة المستخدم
        Clock.schedule_once(lambda dt: self.home_screen.update_peers_list(peers_snapshot))

    # ---------- استقبال رسالة واردة (من خيط السيرفر) ----------
    def _on_message_received(self, payload: dict):
        Clock.schedule_once(functools.partial(self._handle_incoming_message, payload))

    def _handle_incoming_message(self, payload: dict, dt):
        is_group = payload.get("is_group", False)
        sender_ip = payload.get("sender_ip", "unknown")
        key = "GROUP" if is_group else sender_ip

        msg = {
            "sender_name": payload.get("sender_name", "Unknown"),
            "message": payload.get("message", ""),
            "is_me": False,
            "timestamp": time.strftime("%H:%M"),
        }

        self.chat_histories.setdefault(key, []).append(msg)

        # إذا كانت هذه المحادثة مفتوحة حالياً على الشاشة، نعرض الرسالة فوراً
        if self.sm.current == "chat" and self.chat_screen.current_key == key:
            self.chat_screen.append_message(msg)

    # ---------- إرسال رسالة (من شاشة المحادثة) ----------
    def send_message(self, peer_data: dict, text: str):
        is_group = peer_data.get("is_group", False)
        key = "GROUP" if is_group else peer_data.get("ip")

        msg = {
            "sender_name": self.device_name,
            "message": text,
            "is_me": True,
            "timestamp": time.strftime("%H:%M"),
        }
        self.chat_histories.setdefault(key, []).append(msg)
        self.chat_screen.append_message(msg)  # عرض فوري في الواجهة (Optimistic UI)

        # الإرسال الفعلي عبر الشبكة يتم في خيط منفصل حتى لا يُجمّد الواجهة
        threading.Thread(
            target=self._dispatch_message,
            args=(peer_data, text),
            daemon=True,
        ).start()

    def _dispatch_message(self, peer_data: dict, text: str):
        if peer_data.get("is_group"):
            peer_ips = list(self.discovery.active_peers.keys())
            ChatClient.send_group_message(peer_ips, self.device_name, text)
        else:
            ChatClient.send_message(peer_data["ip"], self.device_name, text)


if __name__ == "__main__":
    AirChatApp().run()