# ui/components/chat_bubble.py
"""
مكوّن فقاعة رسالة واحدة داخل شاشة المحادثة.
يتم عرضه كصف كامل العرض، مع محاذاة الفقاعة نفسها يميناً لرسائلي
ويساراً لرسائل الطرف الآخر.
"""

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp

from config.settings import (
    COLOR_BUBBLE_ME, COLOR_BUBBLE_OTHER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
)


class ChatBubble(MDBoxLayout):
    """صف كامل العرض يحتوي فقاعة رسالة واحدة، مع محاذاة تلقائية."""

    def __init__(self, text: str, sender_name: str, is_me: bool = False,
                 timestamp: str = "", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.padding = (dp(10), dp(4))

        bubble = MDBoxLayout(
            orientation='vertical',
            size_hint=(0.72, None),
            padding=(dp(12), dp(8)),
            spacing=dp(2),
        )

        bubble_color = COLOR_BUBBLE_ME if is_me else COLOR_BUBBLE_OTHER
        with bubble.canvas.before:
            Color(*bubble_color)
            bg = RoundedRectangle(pos=bubble.pos, size=bubble.size, radius=[dp(14)])

        def _update_bg(instance, _value):
            bg.pos = instance.pos
            bg.size = instance.size

        bubble.bind(pos=_update_bg, size=_update_bg)

        # اسم المرسل (فقط لرسائل الطرف الآخر)
        if not is_me:
            name_lbl = MDLabel(
                text=sender_name,
                theme_text_color="Custom",
                text_color=COLOR_TEXT_SECONDARY,
                bold=True,
                font_style="Label",
                size_hint_y=None,
                height=dp(16),
            )
            bubble.add_widget(name_lbl)

        # نص الرسالة (مع التفاف تلقائي للسطر)
        msg_lbl = MDLabel(
            text=text,
            theme_text_color="Custom",
            text_color=COLOR_TEXT_PRIMARY,
            size_hint_y=None,
        )
        msg_lbl.bind(
            width=lambda inst, w: setattr(inst, 'text_size', (w, None)),
            texture_size=lambda inst, ts: setattr(inst, 'height', ts[1]),
        )
        bubble.add_widget(msg_lbl)

        # الوقت
        if timestamp:
            time_lbl = MDLabel(
                text=timestamp,
                theme_text_color="Custom",
                text_color=COLOR_TEXT_SECONDARY,
                font_style="Label",
                size_hint_y=None,
                height=dp(14),
                halign="right",
            )
            bubble.add_widget(time_lbl)

        bubble.bind(minimum_height=bubble.setter('height'))
        bubble.bind(height=lambda inst, h: setattr(self, 'height', h + dp(8)))

        spacer = Widget(size_hint_x=0.28)

        if is_me:
            self.add_widget(spacer)
            self.add_widget(bubble)
        else:
            self.add_widget(bubble)
            self.add_widget(spacer)