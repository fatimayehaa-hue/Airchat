# utils/arabic_support.py
"""
دعم عرض اللغة العربية بشكل صحيح داخل Kivy.

مكتبة Kivy لا تقوم تلقائياً بـ:
  1) تشكيل الحروف العربية (وصل الحروف ببعضها البعض بالشكل الصحيح)
  2) ترتيب النص من اليمين لليسار (RTL)

لذلك نستخدم مكتبتي arabic_reshaper و python-bidi لمعالجة أي نص عربي
قبل عرضه، بالإضافة لتسجيل خط يحتوي فعلياً على الحروف العربية.
"""

import os
import arabic_reshaper
from bidi.algorithm import get_display
from kivy.core.text import LabelBase

ARABIC_FONT_NAME = "ArabicFont"

_FONT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "fonts", "Cairo-Regular.ttf"
)

_font_registered = False


def register_arabic_font():
    """تسجيل خط عربي ليصبح متاحاً في التطبيق باسم ARABIC_FONT_NAME.
    يجب استدعاء هذه الدالة مرة واحدة عند بدء التطبيق، قبل إنشاء أي واجهة."""
    global _font_registered
    if _font_registered:
        return True

    if os.path.exists(_FONT_PATH):
        LabelBase.register(name=ARABIC_FONT_NAME, fn_regular=_FONT_PATH)
        _font_registered = True
        return True
    else:
        print(f"[Arabic Support] ⚠️ تحذير: لم يتم العثور على ملف الخط في: {_FONT_PATH}")
        print("[Arabic Support] الحروف العربية لن تظهر بشكل صحيح حتى تضيف الخط.")
        return False


def ar(text: str) -> str:
    """
    إعادة تشكيل النص العربي (ربط الحروف ببعضها بالشكل الصحيح)
    وضبط اتجاه القراءة (من اليمين لليسار).

    يُستخدم على أي نص قد يحتوي حروفاً عربية قبل عرضه في أي Label أو زر.
    النصوص غير العربية (إنجليزية/أرقام) تمر دون أي تغيير.
    """
    if not text:
        return text
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text