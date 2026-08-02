# ui/screens/home_screen.py
"""
الشاشة الرئيسية: تعرض اسم الشبكة الحالية، وقائمة حية بكل الأجهزة المتصلة،
بالإضافة لزر الدخول إلى قناة المجموعة العامة.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse
from kivy.metrics import dp

from utils.network_info import get_network_name
from utils.arabic_support import ar, ARABIC_FONT_NAME
from config.settings import (
    COLOR_BG_DARK, COLOR_TOPBAR, COLOR_ACCENT, COLOR_ACCENT_DARK,
    COLOR_CARD, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_GROUP, COLOR_ONLINE_DOT,
)


class HomeScreen(MDScreen):
    def __init__(self, on_user_select_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.on_user_select_callback = on_user_select_callback

        # --- الخلفية العامة ---
        with self.canvas.before:
            Color(*COLOR_BG_DARK)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        root = MDBoxLayout(orientation='vertical')

        # --- الشريط العلوي ---
        top_bar = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(72),
            padding=(dp(16), dp(10)),
        )
        with top_bar.canvas.before:
            Color(*COLOR_TOPBAR)
            self.bar_rect = Rectangle(pos=top_bar.pos, size=top_bar.size)
        top_bar.bind(pos=self._update_bar, size=self._update_bar)

        title_lbl = MDLabel(
            text="📡  AirChat",
            bold=True,
            theme_text_color="Custom",
            text_color=COLOR_TEXT_PRIMARY,
            font_style="Title",
            size_hint_y=None,
            height=dp(30),
        )
        title_lbl.font_name = ARABIC_FONT_NAME  # يُضبط بعد الإنشاء حتى لا يُلغيه font_style

        self.network_lbl = MDLabel(
            text=f"🌐  {get_network_name()}",
            theme_text_color="Custom",
            text_color=COLOR_TEXT_SECONDARY,
            font_style="Label",
            size_hint_y=None,
            height=dp(20),
        )
        self.network_lbl.font_name = ARABIC_FONT_NAME

        top_bar.add_widget(title_lbl)
        top_bar.add_widget(self.network_lbl)
        root.add_widget(top_bar)

        # --- قسم "الأفراد والمجموعات" ---
        section_lbl = MDLabel(
            text=ar("الأجهزة والمحادثات"),
            theme_text_color="Custom",
            text_color=COLOR_TEXT_SECONDARY,
            halign="right",
            bold=True,
            size_hint_y=None,
            height=dp(36),
            padding=(dp(16), 0),
        )
        section_lbl.font_name = ARABIC_FONT_NAME
        section_lbl.bind(width=lambda inst, w: setattr(inst, 'text_size', (w - dp(32), None)))
        root.add_widget(section_lbl)

        # --- القائمة القابلة للتمرير ---
        scroll = ScrollView(bar_width=dp(4))
        self.users_list = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(10),
            padding=(dp(12), dp(4), dp(12), dp(16)),
        )
        self.users_list.bind(minimum_height=self.users_list.setter('height'))
        scroll.add_widget(self.users_list)
        root.add_widget(scroll)

        self.add_widget(root)

        # عرض أولي: زر المجموعة فقط + رسالة بحث
        self.update_peers_list({})

    # ---------- تحديث الخلفيات عند تغيّر الحجم ----------
    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def _update_bar(self, instance, value):
        self.bar_rect.pos = instance.pos
        self.bar_rect.size = instance.size

    def refresh_network_name(self):
        self.network_lbl.text = f"🌐  {get_network_name()}"

    # ---------- تحديث قائمة الأجهزة (يُستدعى من التطبيق الرئيسي) ----------
    def update_peers_list(self, active_peers: dict):
        self.users_list.clear_widgets()

        # أ) زر القناة العامة (المجموعة)
        self.users_list.add_widget(self._build_card(
            icon="📢",
            title=ar("القناة العامة"),
            subtitle=ar("محادثة جماعية مع كل المتصلين"),
            bg_color=COLOR_GROUP,
            on_press=lambda: self._select_user({
                "name": "القناة العامة",
                "ip": "GROUP",
                "is_group": True,
            }),
            show_dot=False,
        ))

        # ب) عرض بقية الأجهزة المكتشفة
        if not active_peers:
            empty_lbl = MDLabel(
                text=ar("🔍  جاري البحث عن أجهزة قريبة..."),
                theme_text_color="Custom",
                text_color=COLOR_TEXT_SECONDARY,
                halign="center",
                size_hint_y=None,
                height=dp(50),
            )
            empty_lbl.font_name = ARABIC_FONT_NAME
            self.users_list.add_widget(empty_lbl)
        else:
            for ip, peer_data in sorted(active_peers.items(), key=lambda kv: kv[1].get("name", "")):
                device_name = peer_data.get("name", "Unknown Device")
                self.users_list.add_widget(self._build_card(
                    icon="📱",
                    title=ar(device_name),
                    subtitle=ip,
                    bg_color=COLOR_CARD,
                    on_press=lambda p=peer_data: self._select_user(p),
                    show_dot=True,
                ))

    # ---------- بناء بطاقة جهاز/مجموعة قابلة للنقر ----------
    def _build_card(self, icon, title, subtitle, bg_color, on_press, show_dot):
        card = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(64),
            padding=(dp(14), dp(8)),
            spacing=dp(12),
        )

        with card.canvas.before:
            Color(*bg_color)
            bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])

            if show_dot:
                Color(*COLOR_ONLINE_DOT)
                dot = Ellipse(pos=(card.x, card.y), size=(dp(10), dp(10)))

        def _update_bg(instance, _value):
            bg.pos = instance.pos
            bg.size = instance.size
            if show_dot:
                dot.pos = (instance.right - dp(20), instance.top - dp(20))

        card.bind(pos=_update_bg, size=_update_bg)

        icon_lbl = MDLabel(
            text=icon,
            font_style="Headline",
            size_hint_x=None,
            width=dp(36),
            halign="center",
        )

        text_box = MDBoxLayout(orientation='vertical')
        title_lbl = MDLabel(
            text=title,
            bold=True,
            theme_text_color="Custom",
            text_color=COLOR_TEXT_PRIMARY,
            font_style="Body",
            halign="right",
            shorten=True,
        )
        title_lbl.font_name = ARABIC_FONT_NAME
        title_lbl.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))

        subtitle_lbl = MDLabel(
            text=subtitle,
            theme_text_color="Custom",
            text_color=COLOR_TEXT_SECONDARY,
            font_style="Label",
            halign="right",
            shorten=True,
        )
        subtitle_lbl.font_name = ARABIC_FONT_NAME
        subtitle_lbl.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))

        text_box.add_widget(title_lbl)
        text_box.add_widget(subtitle_lbl)

        card.add_widget(icon_lbl)
        card.add_widget(text_box)

        # جعل البطاقة قابلة للنقر بالكامل
        card.bind(on_touch_up=lambda inst, touch: self._on_card_touch(inst, touch, on_press))
        return card

    def _on_card_touch(self, instance, touch, on_press):
        if instance.collide_point(*touch.pos) and touch.grab_current is None:
            on_press()
            return True
        return False

    def _select_user(self, peer_data):
        if self.on_user_select_callback:
            self.on_user_select_callback(peer_data)
