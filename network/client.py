# network/client.py
"""
عميل إرسال الرسائل (TCP Client)
مسؤول عن فتح اتصال مباشر مع مستخدم آخر وإرسال الرسائل الفردية أو المجموعات.
"""

import socket
import json
from config.settings import TCP_CHAT_PORT


class ChatClient:
    @staticmethod
    def send_message(target_ip: str, sender_name: str, message_text: str, is_group: bool = False,
                     group_id: str = None) -> bool:
        """
        إرسال رسالة مباشرة إلى IP محدد عبر TCP.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3.0)  # وقت الانتظار أقصاه 3 ثوانٍ
            sock.connect((target_ip, TCP_CHAT_PORT))

            payload = {
                "sender_name": sender_name,
                "message": message_text,
                "is_group": is_group,
                "group_id": group_id
            }

            sock.sendall(json.dumps(payload).encode('utf-8'))
            sock.close()
            return True
        except Exception as e:
            print(f"[Client Error] Failed to send message to {target_ip}: {e}")
            return False