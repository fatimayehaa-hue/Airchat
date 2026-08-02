# network/discovery.py
"""
وحدة الاكتشاف البثي (UDP Peer Discovery)
تعلن عن وجود الجهاز على الشبكة، تستقبل إشارات الأجهزة الأخرى،
وتراقب باستمرار الأجهزة التي انقطعت عن الشبكة لإزالتها تلقائياً من القائمة.
"""

import socket
import json
import time
import threading
from config.settings import (
    UDP_BROADCAST_PORT, DISCOVERY_INTERVAL, BUFFER_SIZE,
    PEER_TIMEOUT, CLEANUP_INTERVAL,
)
from utils.network_info import get_local_ip


class PeerDiscovery:
    def __init__(self, device_name: str, on_peers_updated_callback=None):
        self.device_name = device_name
        self.my_ip = get_local_ip()
        self.on_peers_updated_callback = on_peers_updated_callback

        self.active_peers = {}  # {ip: {"name": ..., "ip": ..., "last_seen": ...}}
        self._lock = threading.Lock()
        self.is_running = False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        """بدء خيوط العمل: إرسال البث، الاستماع، وتنظيف الأجهزة المنقطعة."""
        self.is_running = True
        self.sock.bind(('', UDP_BROADCAST_PORT))

        threading.Thread(target=self._listen_for_peers, daemon=True).start()
        threading.Thread(target=self._broadcast_presence, daemon=True).start()
        threading.Thread(target=self._cleanup_stale_peers, daemon=True).start()

    def _broadcast_presence(self):
        """إرسال إشارة تواجد (Heartbeat) كل عدة ثوانٍ."""
        while self.is_running:
            try:
                message = json.dumps({
                    "type": "DISCOVERY_ANNOUNCE",
                    "device_name": self.device_name,
                    "ip": self.my_ip,
                })
                self.sock.sendto(message.encode('utf-8'), ('<broadcast>', UDP_BROADCAST_PORT))
            except Exception as e:
                print(f"[Discovery Error] Broadcast error: {e}")
            time.sleep(DISCOVERY_INTERVAL)

    def _listen_for_peers(self):
        """الاستماع للرسائل القادمة وتحديث قائمة الأجهزة الفعالة."""
        while self.is_running:
            try:
                data, addr = self.sock.recvfrom(BUFFER_SIZE)
                peer_ip = addr[0]

                if peer_ip == self.my_ip:
                    continue  # إهمال الرسائل القادمة من نفس هذا الجهاز

                payload = json.loads(data.decode('utf-8'))
                if payload.get("type") == "DISCOVERY_ANNOUNCE":
                    peer_name = payload.get("device_name", "Unknown Device")

                    with self._lock:
                        self.active_peers[peer_ip] = {
                            "name": peer_name,
                            "ip": peer_ip,
                            "last_seen": time.time(),
                        }
                        snapshot = dict(self.active_peers)

                    self._notify(snapshot)

            except Exception as e:
                if self.is_running:
                    print(f"[Discovery Error] Listen error: {e}")

    def _cleanup_stale_peers(self):
        """إزالة أي جهاز لم نستقبل منه إشارة تواجد منذ فترة طويلة (خرج من الشبكة)."""
        while self.is_running:
            time.sleep(CLEANUP_INTERVAL)
            now = time.time()
            removed = False

            with self._lock:
                stale_ips = [
                    ip for ip, info in self.active_peers.items()
                    if now - info["last_seen"] > PEER_TIMEOUT
                ]
                for ip in stale_ips:
                    del self.active_peers[ip]
                    removed = True
                snapshot = dict(self.active_peers)

            if removed:
                self._notify(snapshot)

    def _notify(self, snapshot):
        if self.on_peers_updated_callback:
            self.on_peers_updated_callback(snapshot)

    def stop(self):
        """إيقاف كل خدمات الاكتشاف."""
        self.is_running = False
        try:
            self.sock.close()
        except Exception:
            pass
