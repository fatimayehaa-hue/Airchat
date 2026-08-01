# main.py
import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, NoTransition
from ui.screens.home_screen import HomeScreen
from ui.screens.chat_screen import ChatScreen

Window.size = (360, 640)


class AirChatApp(MDApp):
    def build(self):
        self.sm = ScreenManager(transition=NoTransition())

        self.home_screen = HomeScreen(
            name="home",
            on_user_select_callback=self.open_chat
        )
        self.chat_screen = ChatScreen(
            name="chat",
            on_back_callback=self.go_to_home
        )

        self.sm.add_widget(self.home_screen)
        self.sm.add_widget(self.chat_screen)

        return self.sm

    def open_chat(self, peer_data):
        self.chat_screen.set_active_chat(peer_data)
        self.sm.current = "chat"

    def go_to_home(self):
        self.sm.current = "home"


if __name__ == "__main__":
    AirChatApp().run()