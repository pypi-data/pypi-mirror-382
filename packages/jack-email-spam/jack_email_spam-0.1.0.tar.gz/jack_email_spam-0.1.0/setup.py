from setuptools import setup, find_packages
from pathlib import Path

# قراءة README بطريقة آمنة (تتفادى مشاكل when build runs in isolated env)
here = Path(__file__).parent
long_description = ""
readme_file = here / "README.md"
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

setup(
    # اسم الحزمة: lowercase، بدون مسافات، بدون -- مزدوج، لا يبدأ/ينتهي بمسافة
    name="jack-email-spam",          # مثال: غيّره إذا تفضل اسم آخر (مثلاً: jack_spam)
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "user-agent",   # تحققنا أن هذا اسم متوافر على PyPI (انظر المرجع). إذا أردت استخدام اسم مختلف استبدله.
        "pyfiglet",
        "rich",
    ],
    author="Your Name",               # عدّل بياناتك
    author_email="your.email@example.com",
    # تحذير أمني/قانوني: لا تكتب وصفًا يشجّع الرسائل المزعجة. ضع وصفًا مشروعًا مثل "email automation/testing utilities".
    description="Email automation/testing utilities (educational / legitimate use only).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jack-email-spam",  # عدّل الرابط لمستودعك
    license="MIT",  # SPDX short form
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)