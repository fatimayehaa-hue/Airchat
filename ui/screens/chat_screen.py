# ui/screens/chat_screen.py
"""
شاشة المحادثة: تعرض سجل الرسائل مع طرف معيّن (أو المجموعة العامة)،
وتسمح بإرسال رسائل جديدة عبر الشبكة المحلية.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock

from ui.components.chat_bubble import ChatBubble
from utils.arabic_support import ar, ARABIC_FONT_NAME
from config.settings import (
    COLOR_BG_DARK, COLOR_TOPBAR, COLOR_ACCENT, COLOR_ACCENT_DARK,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
)


class ChatScreen(MDScreen):
    def __init__(self, on_back_callback=None, on_send_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.on_back_callback = on_back_callback
        self.on_send_callback = on_send_callback
        self.active_peer = None
        self.current_key = None

        with self.canvas.before:
            Color(*COLOR_BG_DARK)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        root = MDBoxLayout(orientation='vertical')

        # --- الشريط العلوي ---
        top_bar = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            padding=(dp(8), dp(6)),
            spacing=dp(8),
        )
        with top_bar.canvas.before:
            Color(*COLOR_TOPBAR)
            self.bar_rect = Rectangle(pos=top_bar.pos, size=top_bar.size)
        top_bar.bind(pos=self._update_bar, size=self._update_bar)

        back_btn = MDLabel(
            text="⬅",
            theme_text_color="Custom",
            text_color=COLOR_ACCENT,
            font_style="Headline",
            size_hint_x=None,
            width=dp(40),
            halign="center",
        )
        back_btn.bind(on_touch_up=self._on_back_touch)

        self.title_label = MDLabel(
            text=ar("محادثة"),
            bold=True,
            theme_text_color="Custom",
            text_color=COLOR_TEXT_PRIMARY,
            font_style="Title",
            halign="right",
        )
        self.title_label.font_name = ARABIC_FONT_NAME
        self.title_label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))

        top_bar.add_widget(back_btn)
        top_bar.add_widget(self.title_label)
        root.add_widget(top_bar)

        # --- منطقة الرسائل ---
        self.scroll = ScrollView(bar_width=dp(4))
        self.messages_list = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(4),
            padding=(0, dp(10)),
        )
        self.messages_list.bind(minimum_height=self.messages_list.setter('height'))
        self.scroll.add_widget(self.messages_list)
        root.add_widget(self.scroll)

        # --- منطقة الإدخال ---
        input_box = MDBoxLayout(
            size_hint_y=None,
            height=dp(58),
            padding=(dp(10), dp(8)),
            spacing=dp(8),
        )
        with input_box.canvas.before:
            Color(*COLOR_TOPBAR)
            self.input_rect = Rectangle(pos=input_box.pos, size=input_box.size)
        input_box.bind(pos=self._update_input_bg, size=self._update_input_bg)

        self.msg_input = MDTextField(
            hint_text=ar("اكتب رسالة..."),
            mode="outlined",
            halign="right",
        )
        self.msg_input.font_name = ARABIC_FONT_NAME
        self.msg_input.bind(on_text_validate=lambda x: self.send_message())

        send_lbl = MDLabel(
            text="➤",
            theme_text_color="Custom",
            text_color=COLOR_ACCENT,
            font_style="Headline",
            size_hint_x=None,
            width=dp(44),
            halign="center",
        )
        send_lbl.bind(on_touch_up=self._on_send_touch)

        input_box.add_widget(self.msg_input)
        input_box.add_widget(send_lbl)
        root.add_widget(input_box)

        self.add_widget(root)

    # ---------- تحديث الخلفيات ----------
    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def _update_bar(self, instance, value):
        self.bar_rect.pos = instance.pos
        self.bar_rect.size = instance.size

    def _update_input_bg(self, instance, value):
        self.input_rect.pos = instance.pos
        self.input_rect.size = instance.size

    def _on_back_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self._go_back()
            return True
        return False

    def _on_send_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.send_message()
            return True
        return False

    # ---------- فتح محادثة مع طرف معيّن ----------
    def set_active_chat(self, peer_data: dict, history: list):
        self.active_peer = peer_data
        self.current_key = "GROUP" if peer_data.get("is_group") else peer_data.get("ip")

        icon = "📢" if peer_data.get("is_group") else "📱"
        self.title_label.text = ar(f"{icon}  {peer_data.get('name', 'محادثة')}")

        self.messages_list.clear_widgets()
        for msg in history:
            self._render_message(msg)
        self._scroll_to_bottom()

    # ---------- إرسال رسالة ----------
    def send_message(self):
        text = self.msg_input.text.strip()
        if not text or not self.active_peer:
            return

        self.msg_input.text = ""

        if self.on_send_callback:
            self.on_send_callback(self.active_peer, text)

    # ---------- إضافة رسالة جديدة (محلية أو مستقبَلة) ----------
    def append_message(self, msg: dict):
        self._render_message(msg)
        self._scroll_to_bottom()

    def _render_message(self, msg: dict):
        bubble = ChatBubble(
            text=ar(msg.get("message", "")),
            sender_name=ar(msg.get("sender_name", "Unknown")),
            is_me=msg.get("is_me", False),
            timestamp=msg.get("timestamp", ""),
        )
        self.messages_list.add_widget(bubble)

    def _scroll_to_bottom(self):
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.05)

    def _go_back(self):
        if self.on_back_callback:
            self.on_back_callback()