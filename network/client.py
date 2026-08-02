# network/client.py
"""
عميل إرسال الرسائل (TCP Client)
يرسل الرسائل الفردية مباشرة لجهاز محدد، أو يبث رسالة جماعية لكل الأجهزة المعروفة
حالياً على الشبكة (كل جهاز يستقبلها عبر اتصال TCP منفصل).
"""

import socket
import json
import threading
from config.settings import TCP_CHAT_PORT


class ChatClient:

    @staticmethod
    def send_message(target_ip: str, sender_name: str, message_text: str,
                     is_group: bool = False) -> bool:
        """إرسال رسالة مباشرة إلى IP محدد عبر TCP."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3.0)
            sock.connect((target_ip, TCP_CHAT_PORT))

            payload = {
                "sender_name": sender_name,
                "message": message_text,
                "is_group": is_group,
            }

            sock.sendall(json.dumps(payload).encode('utf-8'))
            sock.close()
            return True
        except Exception as e:
            print(f"[Client Error] Failed to send message to {target_ip}: {e}")
            return False

    @staticmethod
    def send_group_message(peers_ips: list, sender_name: str, message_text: str):
        """
        إرسال رسالة جماعية: تُرسل بالتوازي (Thread مستقل لكل جهاز)
        لكل الأجهزة المعروفة حالياً في الشبكة المحلية.
        """
        for ip in peers_ips:
            threading.Thread(
                target=ChatClient.send_message,
                args=(ip, sender_name, message_text, True),
                daemon=True,
            ).start()
