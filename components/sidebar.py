# ui/components/sidebar.py
"""
مكون القائمة الجانبية (Navigation Drawer)
تتيح للمستخدم تغيير اسم جهازه والتحكم في وضع المظهر (Dark/Light Mode).
"""

from kivymd.uix.drawer import MDNavigationDrawer
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.app import MDApp


class AppSidebar(MDNavigationDrawer):
    def __init__(self, current_device_name: str, on_name_change_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.on_name_change_callback = on_name_change_callback

        # التخطيط العمودي الرئيسي للقائمة الجانبية
        layout = MDBoxLayout(orientation='vertical', padding=16, spacing=16)

        # 1. ترويسة القائمة الجانبية
        header = MDLabel(
            text="⚙️ الإعدادات",
            font_style="H5",
            size_hint_y=None,
            height="40dp",
            bold=True
        )
        layout.add_widget(header)

        # 2. حقل تغيير اسم الجهاز
        self.name_field = MDTextField(
            text=current_device_name,
            hint_text="اسم جهازك في الشبكة",
            helper_text="هذا الاسم سيظهر للبقية عند اكتشافك",
            helper_text_mode="on_focus",
            size_hint_y=None,
            height="50dp"
        )
        layout.add_widget(self.name_field)

        # زر حفظ الاسم الجديد
        save_btn = MDRaisedButton(
            text="تحديث الاسم",
            size_hint_x=1,
            on_release=self._update_name
        )
        layout.add_widget(save_btn)

        # فاصل
        layout.add_widget(MDBoxLayout(size_hint_y=None, height="20dp"))

        # 3. خيار تغيير المظهر (Dark / Light Mode)
        theme_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="40dp", spacing=10)
        theme_label = MDLabel(text="الوضع الداكن (Dark Mode):")

        app = MDApp.get_running_app()
        is_dark = app.theme_cls.theme_style == "Dark" if app else True

        self.theme_switch = MDSwitch(active=is_dark)
        self.theme_switch.bind(active=self._toggle_theme)

        theme_box.add_widget(theme_label)
        theme_box.add_widget(self.theme_switch)
        layout.add_widget(theme_box)

        # حشو مسافة مرنة في الأسفل دفعاً للعناصر للأعلى
        layout.add_widget(MDBoxLayout())

        self.add_widget(layout)

    def _update_name(self, instance):
        new_name = self.name_field.text.strip()
        if new_name and self.on_name_change_callback:
            self.on_name_change_callback(new_name)

    def _toggle_theme(self, instance, value):
        app = MDApp.get_running_app()
        if app:
            app.theme_cls.theme_style = "Dark" if value else "Light"