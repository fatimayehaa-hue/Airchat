
# ui/screens/chat_screen.py
"""
شاشة المحادثة الفردية والجماعية
عرض الرسائل المتبادلة وإرسال رسائل جديدة مستخدمة واجهات KivyMD.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.clock import Clock


class ChatScreen(MDScreen):
    def init(self, on_back_callback=None, on_send_callback=None, **kwargs):
        super().init(**kwargs)
        self.on_back_callback = on_back_callback
        self.on_send_callback = on_send_callback
        self.target_peer = None  # بيانات الشخص أو المجموعة التي نتحدث معها حالياً

        main_layout = MDBoxLayout(orientation='vertical')

        # 1. الشريط العلوي مع زر العودة
        self.toolbar = MDTopAppBar(
            title="المحادثة",
            left_action_items=[["arrow-right", lambda x: self._go_back()]],
            elevation=2
        )
        main_layout.add_widget(self.toolbar)

        # 2. منطقة عرض الرسائل (Scrollable Area)
        self.scroll_view = MDScrollView()
        self.messages_box = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            padding=10,
            size_hint_y=None
        )
        self.messages_box.bind(minimum_height=self.messages_box.setter('height'))
        self.scroll_view.add_widget(self.messages_box)
        main_layout.add_widget(self.scroll_view)

        # 3. شريط إدخال الرسالة في الأسفل
        input_box = MDBoxLayout(
            orientation='horizontal',
            padding=8,
            spacing=8,
            size_hint_y=None,
            height="60dp"
        )

        self.msg_field = MDTextField(
            hint_text="اكتب رسالتك هنا...",
            mode="round",
            size_hint_x=0.85
        )
        send_btn = MDIconButton(
            icon="send",
            icon_color=[1, 1, 1, 1],
            theme_icon_color="Custom",
            md_bg_color=[0.2, 0.6, 1, 1],
            on_release=self._send_message
        )

        input_box.add_widget(self.msg_field)
        input_box.add_widget(send_btn)
        main_layout.add_widget(input_box)

        self.add_widget(main_layout)

    def set_active_chat(self, peer_data: dict):
        """تجهيز الشاشة للمحادثة المحددة ومسح الرسائل القديمة"""
        self.target_peer = peer_data
        peer_name = peer_data.get("name", peer_data.get("ip", "محادثة"))
        self.toolbar.title = f"💬 {peer_name}"
        self.messages_box.clear_widgets()

    def add_message(self, sender_name: str, text: str, is_me: bool = False):
        """إضافة فقاعة رسالة (Bubble) إلى الشاشة"""
        card = MDCard(
            orientation='vertical',
            padding=10,
            size_hint=(0.75, None),
            size_hint_y=None,
            pos_hint={'right': 0.98} if is_me else {'left': 0.02},
            md_bg_color=[0.2, 0.5, 0.9, 0.8] if is_me else [0.25, 0.25, 0.25, 0.8],
            radius=[12, 12, 0 if is_me else 12, 12 if is_me else 0]
        )

        # اسم المرسل
        sender_label = MDLabel(
            text=sender_name,
            font_style="Caption",
            theme_text_color="Hint",
            size_hint_y=None,
            height="18dp"
        )

        # نص الرسالة
        msg_label = MDLabel(
            text=text,
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            size_hint_y=None
        )
        msg_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))

        card.add_widget(sender_label)
        card.add_widget(msg_label)
        card.height = msg_label.texture_size[1] + 35

        self.messages_box.add_widget(card)

        # النزول لأسفل القائمة تلقائياً لمتابعة أحدث رسالة
        Clock.schedule_once(lambda dt: setattr(self.scroll_view, 'scroll_y', 0), 0.1)

        def _send_message(self, instance):
            text = self.msg_field.text.strip()
            if text and self.target_peer and self.on_send_callback:
                self.on_send_callback(self.target_peer, text)
                self.add_message("أنا", text, is_me=True)
                self.msg_field.text = ""

        def _go_back(self):
            if self.on_back_callback:
                self.on_back_callback()

