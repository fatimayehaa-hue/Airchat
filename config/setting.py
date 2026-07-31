# config/settings.py
"""
ملف الإعدادات الأساسية لتطبيق AirChat
يحتوي على المنافذ (Ports) والثوابت المستخدمة في الشبكة والواجهة.
"""

import os

# --- إعدادات الشبكة (Network Settings) ---
# المنافذ المستخدمة (تأكد من اختيار منافذ غير مستخدمة من النظام)
UDP_BROADCAST_PORT = 50000   # منفذ بث واكتشاف الأجهزة
TCP_CHAT_PORT = 50001        # منفذ استقبال وإرسال الرسائل

# الفاصل الزمني لإرسال إشارة البث (بالثواني)
DISCOVERY_INTERVAL = 3

# حجم التخزين المؤقت للرسائل (Buffer Size)
BUFFER_SIZE = 4096

# --- إعدادات التطبيق الافتراضية ---
DEFAULT_DEVICE_NAME = "AirUser_" + str(os.urandom(2).hex()) # اسم افتراضي للجهاز
DEFAULT_THEME = "Dark"      # المظهر الافتراضي: Dark أو Light