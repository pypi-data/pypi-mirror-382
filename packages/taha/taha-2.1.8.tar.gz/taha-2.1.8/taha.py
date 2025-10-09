# taha.py - نسخه کاملاً محافظت شده
import pygame
import webbrowser
import pyttsx3
import pyperclip
import builtins
import tkinter as tk
from PIL import Image
import requests
from tkinter import colorchooser
import turtle as t
import random as ra
import time
import os
from pathlib import Path
import ctypes
import speech_recognition as sr
import platform
import psutil
import socket
import datetime
import pytz
import random
import string
import jwt
from cryptography.fernet import Fernet
from functools import wraps

print("📦 Taha Library v2.1.6 - Premium Version")

# بارگذاری کلید عمومی RSA برای بررسی JWT
try:
    with open("public_key.pem", "rb") as f:
        public_key = f.read()
    print("✅ کلید عمومی بارگذاری شد")
except FileNotFoundError:
    public_key = None
    print("❌ فایل public_key.pem یافت نشد")

def check_license():
    """بررسی لایسنس - تابع اصلی برای تمام بررسی‌ها"""
    if public_key is None:
        return False, "کلید عمومی یافت نشد"
        
    try:
        with open("buyer_license.jwt", "r") as license_file:
            token = license_file.read().strip()
        jwt.decode(token, public_key, algorithms=["RS256"])
        return True, "لایسنس معتبر است"
    except FileNotFoundError:
        return False, "پرونده‌ی لایسنس یافت نشد"
    except jwt.ExpiredSignatureError:
        return False, "لایسنس منقضی شده است"
    except jwt.InvalidTokenError:
        return False, "لایسنس نامعتبر است"

def premium_required(func):
    """دکوراتور برای توابع پریمیوم"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        is_valid, message = check_license()
        if not is_valid:
            print(f"❌ دسترسی رد شد: {message}")
            print("💡 برای دسترسی به این قابلیت، لایسنس معتبر خریداری کنید")
            return None
        return func(*args, **kwargs)
    return wrapper

# =============================================================================
# توابع پریمیوم - کاملاً محافظت شده
# =============================================================================

class PremiumFeatures:
    """کلاس برای مدیریت توابع پریمیوم با محافظت کامل"""
    
    def __init__(self):
        self._initialized = False
        self._gtts_available = False
        self._transformers_available = False
        
    def _initialize(self):
        """مقداردهی اولیه ماژول‌های پریمیوم"""
        if self._initialized:
            return True
            
        is_valid, message = check_license()
        if not is_valid:
            print(f"❌ امکان مقداردهی: {message}")
            return False
        
        try:
            # بارگذاری ماژول‌های پریمیوم فقط در صورت وجود لایسنس
            from gtts import gTTS, lang as gtts_langs
            from transformers import AutoTokenizer, AutoModelForCausalLM
            self._gtts_available = True
            self._transformers_available = True
            self.gTTS = gTTS
            self.gtts_langs = gtts_langs
            self.AutoTokenizer = AutoTokenizer
            self.AutoModelForCausalLM = AutoModelForCausalLM
            self._initialized = True
            print("✅ ماژول‌های پریمیوم بارگذاری شدند")
            return True
        except ImportError as e:
            print(f"❌ ماژول پریمیوم یافت نشد: {e}")
            return False
    
    @premium_required
    def speak(self, text, lang="auto", speed=1.0, voice_type="female"):
        """تبدیل متن به صوت با قابلیت‌های پیشرفته"""
        if not self._initialize():
            return None
            
        try:
            if lang == "auto":
                lang = "fa" if any('\u0600' <= ch <= '\u06FF' for ch in text) else "en"

            supported_langs = self.gtts_langs.tts_langs()
            if lang not in supported_langs:
                fallback = "ar" if lang == "fa" else "en"
                print(f"[!] زبان '{lang}' توسط gTTS پشتیبانی نمی‌شود. استفاده از جایگزین: '{fallback}'")
                lang = fallback

            downloads = get_downloads_dir()
            downloads.mkdir(parents=True, exist_ok=True)
            filename = get_unique_filename(base_name="voice", ext=".mp3", folder=downloads)

            tts = self.gTTS(text=text, lang=lang, slow=(speed < 1.0))
            tts.save(str(filename))
            
            pygame.mixer.init()
            pygame.mixer.music.load(str(filename))
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play()
            
            estimated_time = len(text) / (10 * speed)
            print(f"🔊 در حال پخش: '{text}' (زمان تقریبی: {estimated_time:.1f} ثانیه)")
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
            print(f"✅ صوت در {filename} ذخیره شد")
            return str(filename)
            
        except Exception as e:
            print(f"خطا در speak پیشرفته: {e}")
            return None

    @premium_required
    def speech_to_text(self, timeout=10, language="fa-IR"):
        """تبدیل صوت به متن با دقت بالا"""
        is_valid, message = check_license()
        if not is_valid:
            return f"❌ نیاز به لایسنس: {message}"
            
        recognizer = sr.Recognizer()
        
        try:
            with sr.Microphone() as source:
                print("🎤 در حال گوش دادن... (صحبت کنید)")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=15)
            
            try:
                text = recognizer.recognize_google(audio, language=language)
                print(f"📝 متن تشخیص داده شده: {text}")
                return text
            except:
                if language != "en-US":
                    text = recognizer.recognize_google(audio, language="en-US")
                    print(f"📝 متن تشخیص داده شده (انگلیسی): {text}")
                    return text
                else:
                    raise
                    
        except sr.WaitTimeoutError:
            return "⏰ زمان گوش دادن به پایان رسید"
        except sr.UnknownValueError:
            return "❌ صدای واضحی تشخیص داده نشد"
        except sr.RequestError as e:
            return f"❌ خطا در سرویس: {e}"
        except Exception as e:
            return f"❌ خطای ناشناخته: {e}"

    @premium_required
    def ai_chat(self, prompt, model="gpt2", max_length=100):
        """چت با هوش مصنوعی محلی"""
        if not self._initialize():
            return "❌ ماژول هوش مصنوعی در دسترس نیست"
            
        try:
            tokenizer = self.AutoTokenizer.from_pretrained(model)
            model_obj = self.AutoModelForCausalLM.from_pretrained(model)
            
            inputs = tokenizer.encode(prompt, return_tensors="pt")
            outputs = model_obj.generate(inputs, max_length=max_length, num_return_sequences=1)
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response
        except Exception as e:
            return f"خطا در هوش مصنوعی: {e}"

    @premium_required
    def encrypt_file(self, file_path, key=None):
        """رمزگذاری پیشرفته فایل‌ها"""
        is_valid, message = check_license()
        if not is_valid:
            print(f"❌ {message}")
            return None
            
        try:
            if key is None:
                key = Fernet.generate_key()
            
            cipher = Fernet(key)
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            encrypted_data = cipher.encrypt(file_data)
            
            encrypted_path = file_path + ".encrypted"
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
            
            print(f"✅ فایل رمزگذاری شد: {encrypted_path}")
            print(f"🔑 کلید رمزگشایی: {key.decode()}")
            return key.decode()
            
        except Exception as e:
            print(f"❌ خطا در رمزگذاری: {e}")
            return None

    @premium_required
    def decrypt_file(self, encrypted_path, key, output_path=None):
        """رمزگشایی فایل‌های رمزگذاری شده"""
        is_valid, message = check_license()
        if not is_valid:
            print(f"❌ {message}")
            return None
            
        try:
            cipher = Fernet(key.encode())
            
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = cipher.decrypt(encrypted_data)
            
            if output_path is None:
                output_path = encrypted_path.replace(".encrypted", ".decrypted")
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            print(f"✅ فایل رمزگشایی شد: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ خطا در رمزگشایی: {e}")
            return None

    @premium_required
    def voice_assistant(self, wake_word="تاحا"):
        """دستیار صوتی هوشمند"""
        is_valid, message = check_license()
        if not is_valid:
            print(f"❌ {message}")
            return
            
        print(f"🎧 دستیار صوتی فعال شد. بگو '{wake_word}' برای شروع...")
        
        while True:
            command = self.speech_to_text(language="fa-IR")
            
            if command and wake_word in command:
                print(f"🔔 دستور تشخیص داده شد: {command}")
                
                if "خاموش" in command or "خداحافظ" in command:
                    self.speak("خداحافظ! موفق باشید")
                    break
                elif "ساعت" in command:
                    current_time = datetime.datetime.now().strftime("%H:%M")
                    self.speak(f"ساعت {current_time} است")
                elif "تاریخ" in command:
                    current_date = today("%Y/%m/%d")
                    self.speak(f"امروز {current_date} است")
                elif "جستجو" in command:
                    query = command.replace("جستجو", "").strip()
                    google_search(query)
                    self.speak(f"در حال جستجو برای {query}")
                else:
                    response = self.ai_chat(command)
                    self.speak(response)
                    
        print("دستیار صوتی غیرفعال شد")

    @premium_required  
    def auto_typer(self, text, speed=0.1):
        """تایپ خودکار متن"""
        is_valid, message = check_license()
        if not is_valid:
            print(f"❌ {message}")
            return
            
        try:
            import pyautogui
            
            print(f"⌨️ در حال تایپ خودکار... (سرعت: {speed} ثانیه)")
            time.sleep(3)
            
            for char in text:
                pyautogui.write(char)
                time.sleep(speed)
            
            print("✅ تایپ خودکار کامل شد")
        except ImportError:
            print("❌ ماژول pyautogui نصب نیست.")

    @premium_required
    def system_optimizer(self):
        """بهینه‌ساز سیستم"""
        is_valid, message = check_license()
        if not is_valid:
            print(f"❌ {message}")
            return False
            
        try:
            print("🔄 در حال بهینه‌سازی سیستم...")
            
            if os.name == 'nt':
                os.system('del /q /f /s %temp%\\*')
                print("✅ فایل‌های موقت پاک شدند")
            
            ram_before = psutil.virtual_memory().percent
            print(f"🎯 استفاده از RAM قبل از بهینه‌سازی: {ram_before}%")
            
            import gc
            gc.collect()
            
            ram_after = psutil.virtual_memory().percent
            print(f"🎯 استفاده از RAM بعد از بهینه‌سازی: {ram_after}%")
            
            self.speak("بهینه‌سازی سیستم با موفقیت انجام شد")
            return True
            
        except Exception as e:
            print(f"❌ خطا در بهینه‌سازی: {e}")
            return False

    @premium_required
    def web_scraper(self, url, extract_images=False):
        """استخراج اطلاعات از وبسایت"""
        is_valid, message = check_license()
        if not is_valid:
            print(f"❌ {message}")
            return None
            
        try:
            response = requests.get(url)
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.title.string if soup.title else "بدون عنوان"
            print(f"📄 عنوان صفحه: {title}")
            
            text_content = soup.get_text()[:500] + "..."
            print(f"📝 محتوای متنی: {text_content}")
            
            results = {"title": title, "content": text_content}
            
            if extract_images:
                images = soup.find_all('img')
                image_urls = [img.get('src') for img in images if img.get('src')]
                results["images"] = image_urls
                print(f"🖼️ تعداد تصاویر یافت شده: {len(image_urls)}")
            
            return results
            
        except Exception as e:
            print(f"❌ خطا در استخراج اطلاعات: {e}")
            return None

# ایجاد نمونه از کلاس پریمیوم
premium = PremiumFeatures()

# =============================================================================
# توابع رایگان - بدون تغییر
# =============================================================================

def to_gray(path, out="gray.png"):
    """تبدیل تصویر به خاکستری"""
    img = Image.open(path).convert("L")
    img.save(out)

def my_ip():
    """دریافت IP عمومی"""
    try:
        return requests.get("https://api.ipify.org").text
    except:
        return "network error"

def today(format="%Y-%m-%d"):
    """دریافت تاریخ امروز"""
    return datetime.datetime.now().strftime(format)

def rename(old, new):
    """تغییر نام فایل"""
    if os.path.exists(old):
        os.rename(old, new)
        return True
    return False

def clear_clipboard():
    """پاک کردن کلیپ‌بورد"""
    pyperclip.copy("")

def random_filename(ext=".mp3", prefix="file"):
    """تولید نام تصادفی برای فایل"""
    return f"{prefix}_{random.randint(1000,9999)}{ext}"

def list_files(folder="."):
    """لیست فایل‌های یک پوشه"""
    return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder,f))]

def to_upper(text):
    """تبدیل متن به حروف بزرگ"""
    return text.upper()

def open_web(url):
    """باز کردن وبسایت در مرورگر"""
    webbrowser.open(url)

def google_search(text):
    """جستجوی گوگل"""
    webbrowser.open(f"https://www.google.com/search?q={text}")

def get_system_summary():
    """دریافت اطلاعات سیستم"""
    try:
        os_info = platform.system() + " " + platform.release()
        cpu_info = platform.processor()
        ram_info = f"{round(psutil.virtual_memory().total / (1024**3))} GB"
        python_ver = platform.python_version()
        ip = socket.gethostbyname(socket.gethostname())
        tz = datetime.datetime.now(pytz.timezone("Asia/Tehran")).tzname()
        return {
            "os": os_info,
            "cpu": cpu_info,
            "ram": ram_info,
            "python_version": python_ver,
            "ip_address": ip,
            "timezone": tz
        }
    except Exception as e:
        return {"error": str(e)}

def generate_password(length=12, strength="strong"):
    """تولید رمز عبور تصادفی"""
    if strength == "simple":
        chars = string.ascii_lowercase
    elif strength == "medium":
        chars = string.ascii_letters + string.digits
    else:
        chars = string.ascii_letters + string.digits + string.punctuation

    return ''.join(random.choice(chars) for _ in range(length))

def browser(url):
    """باز کردن مرورگر"""
    webbrowser.open(url)

def run_app(path):
    """اجرای برنامه"""
    try:
        os.startfile(path)
    except Exception as e:
        print(f"TahaError: {e}")

def get_file_size(path: str):
    """دریافت حجم فایل"""
    size = os.path.getsize(path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

def count_words(text: str):
    """شمارش کلمات متن"""
    return len(text.strip().split())

def get_day_name(date_str: str):
    """دریافت نام روز از تاریخ"""
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%A")
    except ValueError:
        return "Invalid date format"

def get_downloads_dir():
    """دریافت مسیر پوشه دانلودها"""
    return Path(os.path.expanduser("~/Downloads"))

def system(action):
    """کنترل سیستم"""
    if action == "shut_down":
        os.system("shutdown /s /t 0")
    elif action == "restart":
        os.system("shutdown /r /t 1")
    elif action == "log_out":
        os.system("shutdown -l")
    elif action == "sleep":
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def copy_text(text):
    """کپی متن به کلیپ‌بورد"""
    pyperclip.copy(text)

def save_var(local_or_name, value):
    """ذخیره متغیر در فایل"""
    with open(local_or_name, "w") as f:
        f.write(str(value))

def load_var(local_or_name, default=None):
    """بارگذاری متغیر از فایل"""
    try:
        with open(local_or_name, "r") as f:
            data = f.read().strip()
            if data == "":
                return default
            return data
    except FileNotFoundError:
        return default

def ri(a, b):
    """عدد تصادفی بین a و b"""
    return ra.randint(a, b)

def key(a, b):
    """تنظیم کلید برای turtle"""
    t.listen()
    t.onkey(a, b)

def click(a):
    """تنظیم کلیک برای turtle"""
    t.onscreenclick(a)

def getcolor(tit):
    """انتخاب رنگ"""
    return colorchooser.askcolor(title=tit)

def rc(a):
    """انتخاب تصادفی از لیست"""
    return ra.choice(a)

def leftclick(a):
    """کلیک چپ turtle"""
    t.onscreenclick(a, btn=1)

def middleclick(a):
    """کلیک وسط turtle"""
    t.onscreenclick(a, btn=2)

def rightclick(a):
    """کلیک راست turtle"""
    t.onscreenclick(a, btn=3)

def move(x, y):
    """حرکت turtle به مختصات مشخص"""
    t.goto(x, y)

def randcolor():
    """رنگ تصادفی برای turtle"""
    t.colormode(255)
    r = ra.randint(1, 255)
    g = ra.randint(1, 255)
    b = ra.randint(1, 255)
    t.color((r, g, b))

def rgbcolor(r, g, b):
    """رنگ RGB برای turtle"""
    t.colormode(255)
    t.color((r, g, b))

def getping(url):
    """اندازه‌گیری پینگ"""
    start = time.time()
    try:
        requests.get(url)
        end = time.time()
        return round((end - start) * 1000)
    except:
        return -1

def mouseX():
    """موقعیت X ماوس"""
    screen = t.Screen()
    return screen.cv.winfo_pointerx() - screen.cv.winfo_rootx() - screen.window_width() // 2

def mouseY():
    """موقعیت Y ماوس"""
    screen = t.Screen()
    return screen.window_height() // 2 - (screen.cv.winfo_pointery() - screen.cv.winfo_rooty())

def hidecursor():
    """مخفی کردن نشانگر ماوس"""
    ctypes.windll.user32.ShowCursor(False)

def showcursor():
    """نمایش نشانگر ماوس"""
    ctypes.windll.user32.ShowCursor(True)

def shapecursor(a):
    """تغییر شکل نشانگر ماوس"""
    root = tk.Tk()
    root.config(cursor=a)
    root.mainloop()

def convert_jpg(your_format, your_picture_name, your_image_path_or_name):
    """تبدیل فرمت تصویر"""
    img = Image.open(your_image_path_or_name)
    img.save(f"{your_picture_name}.{your_format}")

img_turtle = None

def upload_gif(NameOrPath, sizeWidth, sizeHight):
    """آپلود GIF برای turtle"""
    global img_turtle
    screen = t.Screen()
    screen.register_shape(NameOrPath)
    img_turtle = t.Turtle()
    img_turtle.shape(NameOrPath)
    img_turtle.penup()
    img_turtle.goto(0, 0)
    return img_turtle

def show_picture():
    """نمایش تصویر turtle"""
    global img_turtle
    if img_turtle:
        img_turtle.showturtle()

def hide_picture():
    """مخفی کردن تصویر turtle"""
    global img_turtle
    if img_turtle:
        img_turtle.hideturtle()

def play_mp3(path):
    """پخش فایل MP3"""
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def text_to_speech(text):
    """تبدیل متن به گفتار"""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

def search_real_usage(keyword, path):
    """جستجوی کاربرد واقعی کلمه کلیدی"""
    ignore_patterns = [
        f'def search_keyword_in_project',
        f'search_keyword_in_project("{keyword}"',
        f'search_real_usage("{keyword}"'
    ]

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                with open(full_path, encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, start=1):
                        line_stripped = line.strip()
                        if keyword in line_stripped and not any(p in line_stripped for p in ignore_patterns):
                            print(f"📍 Found in {full_path}, line {i}:\n  {line_stripped}")

def get_unique_filename(base_name="voice", ext=".mp3", folder=None):
    """تولید نام فایل منحصر به فرد"""
    folder = folder or get_downloads_dir()
    i = 0
    while True:
        filename = folder / f"{base_name}_{i}{ext}"
        if not filename.exists():
            return filename
        i += 1

def clock(unit):
    """دریافت زمان"""
    now = datetime.datetime.now()
    if unit == "hour":
        return now.hour
    elif unit == "minute":
        return now.minute
    elif unit == "second":
        return now.second
    elif unit == "microsecond":
        return now.microsecond
    else:
        return "Invalid unit"

# =============================================================================
# اتصال توابع پریمیوم به نام‌های اصلی برای سازگاری
# =============================================================================

# اختصاص توابع پریمیوم به نام‌های اصلی (فقط در صورت وجود لایسنس)
def get_premium_function(name):
    """دریافت تابع پریمیوم در صورت وجود لایسنس"""
    is_valid, message = check_license()
    if not is_valid:
        def premium_locked(*args, **kwargs):
            print(f"❌ تابع '{name}' نیاز به لایسنس دارد: {message}")
            return None
        return premium_locked
    
    # بازگرداندن تابع واقعی در صورت وجود لایسنس
    premium_funcs = {
        'speak': premium.speak,
        'speech_to_text': premium.speech_to_text,
        'ai_chat': premium.ai_chat,
        'encrypt_file': premium.encrypt_file,
        'decrypt_file': premium.decrypt_file,
        'voice_assistant': premium.voice_assistant,
        'auto_typer': premium.auto_typer,
        'system_optimizer': premium.system_optimizer,
        'web_scraper': premium.web_scraper,
    }
    return premium_funcs.get(name)

# ایجاد توابع پریمیوم با بررسی لایسنس
speak = get_premium_function('speak')
speech_to_text = get_premium_function('speech_to_text')
ai_chat = get_premium_function('ai_chat')
encrypt_file = get_premium_function('encrypt_file')
decrypt_file = get_premium_function('decrypt_file')
voice_assistant = get_premium_function('voice_assistant')
auto_typer = get_premium_function('auto_typer')
system_optimizer = get_premium_function('system_optimizer')
web_scraper = get_premium_function('web_scraper')

# لیست کامل قابلیت‌ها
__all__ = [
    # توابع رایگان
    "text_to_speech", "randcolor", "rgbcolor", "upload_gif", "search_real_usage", "showcursor", 
    "count_words", "get_day_name", "get_system_summary", "open_web", "rename", "today",
    "save_var", "load_var", "getping", "clock", "mouseX", "mouseY", "hidecursor", "shapecursor", 
    "run_app", "get_file_size", "generate_password", "google_search", "random_filename", "to_gray", 
    "key", "click", "getcolor", "rc", "ri", "leftclick", "middleclick", "rightclick", "play_mp3", 
    "system", "copy_text", "browser", "to_upper", "list_files", "clear_clipboard", "my_ip",
    "move", "convert_jpg",
    
    # توابع پریمیوم (فقط با لایسنس فعال می‌شوند)
    "speak", "speech_to_text", "ai_chat", "encrypt_file", "decrypt_file", 
    "voice_assistant", "auto_typer", "system_optimizer", "web_scraper",
]
