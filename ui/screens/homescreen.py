# ui/screens/home_screen.py
"""
الشاشة الرئيسية لتطبيق AirChat
تعرض اسم الشبكة المحلية، قائمة المستخدمين النشطين، والمجموعات.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.tab import MDTabsBase, MDTabs
from utils.network_info import get_network_name


class Tab(MDBoxLayout, MDTabsBase):
    """عنصر مخصص لتبويبات الأفراد والمجموعات"""
    pass


class HomeScreen(MDScreen):
    def __init__(self, on_user_select_callback=None, on_drawer_open_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.on_user_select_callback = on_user_select_callback
        self.on_drawer_open_callback = on_drawer_open_callback

        main_layout = MDBoxLayout(orientation='vertical')

        # 1. الشريط العلوى (Top App Bar)
        network_title = get_network_name()
        self.toolbar = MDTopAppBar(
            title=f"📡 {network_title}",
            left_action_items=[["menu", lambda x: self._open_drawer()]],
            elevation=2
        )
        main_layout.add_widget(self.toolbar)

        # 2. نظام التبويبات (Tabs: Users / Groups)
        self.tabs = MDTabs()

        # --- تبويب المتصلين (Users) ---
        self.users_tab = Tab(title="المستخدمين المتصلين", orientation="vertical")
        self.users_scroll = MDScrollView()
        self.users_list = MDList()
        self.users_scroll.add_widget(self.users_list)
        self.users_tab.add_widget(self.users_scroll)

        # --- تبويب المجموعات (Groups) ---
        self.groups_tab = Tab(title="المجموعات", orientation="vertical")
        self.groups_scroll = MDScrollView()
        self.groups_list = MDList()

        # إضافة مجموعة عامة افتراضية لجميع متصلي الشبكة
        default_group = OneLineIconListItem(
            text="📢 المجموعة العامة (Public Channel)",
            on_release=lambda x: self._select_user(
                {"name": "المجموعة العامة", "ip": "255.255.255.255", "is_group": True})
        )
        default_group.add_widget(IconLeftWidget(icon="account-group"))
        self.groups_list.add_widget(default_group)

        self.groups_scroll.add_widget(self.groups_list)
        self.groups_tab.add_widget(self.groups_scroll)

        self.tabs.add_widget(self.users_tab)
        self.tabs.add_widget(self.groups_tab)

        main_layout.add_widget(self.tabs)
        self.add_widget(main_layout)

    def update_peers_list(self, active_peers: dict):
        """تحديث قائمة الأجهزة المتصلة بمرونة في الواجهة"""
        self.users_list.clear_widgets()

        if not active_peers:
            empty_item = OneLineIconListItem(text="جاري البحث عن أجهزة مجاورة...")
            empty_item.add_widget(IconLeftWidget(icon="radar"))
            self.users_list.add_widget(empty_item)
            return

        for ip, peer_data in active_peers.items():
            device_name = peer_data.get("name", "جهاز غير معروف")
            item = OneLineIconListItem(
                text=f"{device_name} ({ip})",
                on_release=lambda x, p=peer_data: self._select_user(p)
            )
            item.add_widget(IconLeftWidget(icon="cellphone-wireless"))
            self.users_list.add_widget(item)

    def _select_user(self, peer_data):
        if self.on_user_select_callback:
            self.on_user_select_callback(peer_data)

    def _open_drawer(self):
        if self.on_drawer_open_callback:
            self.on_drawer_open_callback()