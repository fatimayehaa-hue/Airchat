# utils/network_info.py
"""
دوال مساعدة لاستخراج معلومات الشبكة الحالية (IP Address & SSID)
"""

import socket


def get_local_ip() -> str:
    """استخراج عنوان الـ IP المحلي للجهاز على الشبكة."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # لا يتم إجراء اتصال فعلي خارجي، فقط لتحديد الواجهة المستعملة للشبكة المحلية
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def get_network_name() -> str:
    """استخراج اسم شبكة الـ Wi-Fi الحالية (أو تمثيل مبسّط للنطاق المحلي)."""
    try:
        ip = get_local_ip()
        if ip.startswith("127."):
            return "Disconnected / Offline"
        subnet = ".".join(ip.split(".")[:3]) + ".x"
        return f"Local Wi-Fi Network ({subnet})"
    except Exception:
        return "Unknown Network"