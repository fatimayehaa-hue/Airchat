# ui/screens/chat_screen.py
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFabButton, MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import MDList
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.label import Label
from kivy.clock import Clock


class ChatScreen(MDScreen):
    def __init__(self, on_back_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.on_back_callback = on_back_callback
        self.active_peer = None

        main_layout = MDBoxLayout(orientation='vertical', spacing=5)

        # الشريط العلوي
        self.top_bar = MDBoxLayout(
            size_hint_y=None,
            height="50dp",
            md_bg_color=[0.12, 0.15, 0.2, 1],
            padding=[10, 0]
        )

        back_btn = MDButton(
            MDButtonText(text="< Back"),
            on_release=lambda x: self._go_back()
        )
        self.title_label = Label(text="Chat", bold=True, color=(1, 1, 1, 1))

        self.top_bar.add_widget(back_btn)
        self.top_bar.add_widget(self.title_label)
        main_layout.add_widget(self.top_bar)

        # منطقة الرسائل
        scroll = MDScrollView()
        self.messages_list = MDList()
        scroll.add_widget(self.messages_list)
        main_layout.add_widget(scroll)

        # منطقة الإدخال
        input_box = MDBoxLayout(size_hint_y=None, height="60dp", padding=5, spacing=5)
        self.msg_input = MDTextField(hint_text="Type a message...")
        send_btn = MDButton(
            MDButtonText(text="Send"),
            on_release=lambda x: self.send_message()
        )

        input_box.add_widget(self.msg_input)
        input_box.add_widget(send_btn)
        main_layout.add_widget(input_box)

        self.add_widget(main_layout)

    def set_active_chat(self, peer_data):
        self.active_peer = peer_data
        name = peer_data.get("name", "Chat")
        self.title_label.text = f"Chat: {name}"

    def send_message(self):
        msg = self.msg_input.text.strip()
        if msg:
            # إضافة الرسالة للقائمة
            self.msg_input.text = ""

    def _go_back(self):
        if self.on_back_callback:
            self.on_back_callback()