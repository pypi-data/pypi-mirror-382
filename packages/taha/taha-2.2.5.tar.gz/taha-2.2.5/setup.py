from setuptools import setup, find_packages

setup(
    name="taha",
    version="2.2.5",
    author="Taha",
    description="📦 Taha Library - Premium Edition with voice, AI, and tools",
    packages=find_packages(),
    py_modules=["taha"],
    install_requires=[
        "pygame",
        "requests",
        "pyttsx3",
        "pyperclip",
        "pillow",
        "speechrecognition",
        "cryptography",
        "transformers",
        "psutil",
        "pytz",
        "jwt",
        "beautifulsoup4",
        "pyautogui",
        "gTTS",
    ],
    python_requires=">=3.8",
)
