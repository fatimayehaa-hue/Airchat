# network/discovery.py
"""
وحدة الاكتشاف البثي (UDP Peer Discovery)
تتيح للجهاز الإعلان عن وجوده للشبكة واستقبال إشارات الأجهزة الأخرى المتصلة.
"""

import socket
import json
import time
import threading
from config.settings import UDP_BROADCAST_PORT, DISCOVERY_INTERVAL, BUFFER_SIZE
from utils.network_info import get_local_ip


class PeerDiscovery:
    def __init__(self, device_name: str, on_peer_found_callback=None):
        self.device_name = device_name
        self.my_ip = get_local_ip()
        self.on_peer_found_callback = on_peer_found_callback

        self.active_peers = {}  # قاموس لحفظ الأجهزة المتصلة: {ip: {"name": ..., "last_seen": ...}}
        self.is_running = False

        # إعداد سوكيت البث (UDP Socket)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        """بدء خيوط العمل (Threads) لإرسال واستقبال البث في الخلفية"""
        self.is_running = True
        self.sock.bind(('', UDP_BROADCAST_PORT))

        # خيط لاستقبال الإشارات من الأجهزة الأخرى
        threading.Thread(target=self._listen_for_peers, daemon=True).start()
        # خيط لإرسال إشارة تواجد الجهاز دورياً
        threading.Thread(target=self._broadcast_presence, daemon=True).start()

    def _broadcast_presence(self):
        """إرسال إشارة بث (Heartbeat) كل عدة ثوانٍ"""
        while self.is_running:
            try:
                message = json.dumps({
                    "type": "DISCOVERY_ANNOUNCE",
                    "device_name": self.device_name,
                    "ip": self.my_ip
                })
                # الإرسال لجميع الأجهزة على الشبكة المحلية
                self.sock.sendto(message.encode('utf-8'), ('<broadcast>', UDP_BROADCAST_PORT))
            except Exception as e:
                print(f"[Discovery Error] Broadcast error: {e}")
            time.sleep(DISCOVERY_INTERVAL)

    def _listen_for_peers(self):
        """الاستماع للرسائل القادمة وتحديث قائمة الأجهزة الفعالة"""
        while self.is_running:
            try:
                data, addr = self.sock.recvfrom(BUFFER_SIZE)
                peer_ip = addr[0]

                # إهمال الرسائل القادمة من نفس هذا الجهاز
                if peer_ip == self.my_ip:
                    continue

                payload = json.loads(data.decode('utf-8'))
                if payload.get("type") == "DISCOVERY_ANNOUNCE":
                    peer_name = payload.get("device_name", "Unknown")

                    # حفظ الجهاز في القائمة وتحديث وقت آخر ظهور
                    self.active_peers[peer_ip] = {
                        "name": peer_name,
                        "ip": peer_ip,
                        "last_seen": time.time()
                    }

                    # استدعاء دالة التحديث (Callback) لإعلام الواجهة الرئيسية بالشبكة
                    if self.on_peer_found_callback:
                        self.on_peer_found_callback(self.active_peers)

            except Exception as e:
                if self.is_running:
                    print(f"[Discovery Error] Listen error: {e}")

    def stop(self):
        """إيقاف خدمات الاكتشاف"""
        self.is_running = False
        self.sock.close()