# network/server.py
"""
سيرفر استقبال الرسائل (TCP Server)
يعمل في الخلفية للاستماع المباشر للرسائل الواردة من المستخدمين الآخرين.
"""

import socket
import json
import threading
from config.settings import TCP_CHAT_PORT, BUFFER_SIZE


class ChatServer:
    def __init__(self, on_message_received_callback=None):
        self.on_message_received_callback = on_message_received_callback
        self.is_running = False

        # إنشاء سوكيت TCP للاستماع
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        """بدء تشغيل السيرفر في خيط عمل مستقل (Thread)"""
        self.is_running = True
        self.sock.bind(('', TCP_CHAT_PORT))
        self.sock.listen(5)

        threading.Thread(target=self._listen_for_connections, daemon=True).start()

    def _listen_for_connections(self):
        """الاستماع للاتصالات القادمة من الأجهزة الأخرى"""
        while self.is_running:
            try:
                client_socket, addr = self.sock.accept()
                threading.Thread(target=self._handle_client, args=(client_socket, addr), daemon=True).start()
            except Exception as e:
                if self.is_running:
                    print(f"[Server Error] Accept error: {e}")

    def _handle_client(self, client_socket, addr):
        """معالجة الرسالة القادمة من العميل قراءة وتحليلاً"""
        try:
            data = client_socket.recv(BUFFER_SIZE)
            if data:
                payload = json.loads(data.decode('utf-8'))

                # استدعاء دالة العرض في الواجهة عند وصول رسالة
                if self.on_message_received_callback:
                    self.on_message_received_callback(payload)
        except Exception as e:
            print(f"[Server Error] Handle client error: {e}")
        finally:
            client_socket.close()

    def stop(self):
        """إيقاف السيرفر"""
        self.is_running = False
        self.sock.close()