# ui/screens/home_screen.py
from kivymd.uix.screen import MDScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle


class HomeScreen(MDScreen):
    def __init__(self, on_user_select_callback=None, on_drawer_open_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.on_user_select_callback = on_user_select_callback
        self.on_drawer_open_callback = on_drawer_open_callback

        # 1. إجبار بطاقة الشاشة على رسم خلفية زرقاء داكنة
        with self.canvas.before:
            Color(0.08, 0.12, 0.18, 1)  # خلفية داكنة وأنيقة
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        # 2. التخطيط الرئيسي
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 3. الشريط العلوي (Top Bar)
        top_bar = BoxLayout(size_hint_y=None, height=50, spacing=10)
        with top_bar.canvas.before:
            Color(0.15, 0.25, 0.4, 1)  # أزرق مميز للشريط
            self.bar_rect = Rectangle(pos=top_bar.pos, size=top_bar.size)
        top_bar.bind(pos=self._update_bar, size=self._update_bar)

        title_lbl = Label(
            text="AirChat - Local Network",
            font_size='18sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        top_bar.add_widget(title_lbl)
        main_layout.add_widget(top_bar)

        # 4. قائمة العناصر والتمرير
        scroll = ScrollView()
        self.users_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.users_list.bind(minimum_height=self.users_list.setter('height'))

        scroll.add_widget(self.users_list)
        main_layout.add_widget(scroll)

        self.add_widget(main_layout)

        # عرض القائمة
        self.update_peers_list({})

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def _update_bar(self, instance, value):
        self.bar_rect.pos = instance.pos
        self.bar_rect.size = instance.size

    def update_peers_list(self, active_peers: dict):
        self.users_list.clear_widgets()

        # أ) زر القناة العامة
        group_btn = Button(
            text="📢  Public Group Channel",
            size_hint_y=None,
            height=60,
            background_color=(0.1, 0.6, 0.3, 1),
            font_size='16sp',
            bold=True
        )
        group_btn.bind(on_release=lambda x: self._select_user({
            "name": "Public Group",
            "ip": "255.255.255.255",
            "is_group": True
        }))
        self.users_list.add_widget(group_btn)

        # ب) عرض بقية الأجهزة
        if not active_peers:
            status_lbl = Label(
                text="🔍 Searching for nearby devices...",
                size_hint_y=None,
                height=50,
                color=(0.7, 0.7, 0.7, 1)
            )
            self.users_list.add_widget(status_lbl)
        else:
            for ip, peer_data in active_peers.items():
                device_name = peer_data.get("name", "Unknown Device")
                btn = Button(
                    text=f"📱  {device_name} ({ip})",
                    size_hint_y=None,
                    height=55,
                    background_color=(0.2, 0.3, 0.45, 1)
                )
                btn.bind(on_release=lambda x, p=peer_data: self._select_user(p))
                self.users_list.add_widget(btn)

    def _select_user(self, peer_data):
        if self.on_user_select_callback:
            self.on_user_select_callback(peer_data)