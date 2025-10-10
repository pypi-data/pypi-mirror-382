import time
import datetime
import os

__all__ = [
    # أوامر time الأصلية
    "sleep", "time_", "ctime", "gmtime", "localtime",
    "mktime", "strftime", "strptime", "asctime", "perf_counter",
    "process_time", "monotonic", "thread_time", "get_clock_info",

    # دوال مصنوعة بإيدينا
    "pause_until", "measure_execution_time", "countdown", "stopwatch",
    "delay_message", "wait_until_date", "time_difference",
    "timer_with_callback", "save_log_time", "show_system_uptime",
    "wait_for_input", "repeat_every", "real_clock",
    "display_time_animation"
]

# ----------------------------------------------------------
# 🧩 أوامر مكتبة time الأصلية (بأسماء واضحة)
# ----------------------------------------------------------

def sleep(seconds):
    """إيقاف البرنامج لعدد معين من الثواني"""
    time.sleep(seconds)


def time_():
    """ترجع الوقت الحالي كعدد ثواني من 1970"""
    return time.time()


def ctime(secs=None):
    """ترجع الوقت الحالي في شكل نص منسق"""
    return time.ctime(secs)


def gmtime(secs=None):
    """ترجع الوقت العالمي UTC"""
    return time.gmtime(secs)


def localtime(secs=None):
    """ترجع الوقت المحلي"""
    return time.localtime(secs)


def mktime(t):
    """تحوّل struct_time لثواني"""
    return time.mktime(t)


def strftime(format_string="%Y-%m-%d %H:%M:%S", t=None):
    """تحويل الوقت إلى نص منسق"""
    if t is None:
        t = time.localtime()
    return time.strftime(format_string, t)


def strptime(string, format_string):
    """تحويل نص وقت إلى struct_time"""
    return time.strptime(string, format_string)


def asctime(t=None):
    """تحويل struct_time إلى نص"""
    if t is None:
        t = time.localtime()
    return time.asctime(t)


def perf_counter():
    """عدّاد دقيق لحساب مدة تنفيذ الكود"""
    return time.perf_counter()


def process_time():
    """وقت تنفيذ العمليات (CPU time)"""
    return time.process_time()


def monotonic():
    """ساعة monotonic لا تتأثر بتغيير الوقت"""
    return time.monotonic()


def thread_time():
    """وقت تنفيذ الثريد (Thread execution time)"""
    return time.thread_time()


def get_clock_info(name):
    """معلومات عن أي ساعة داخل time"""
    return time.get_clock_info(name)


# ----------------------------------------------------------
# ⚙️ دوال مصنوعة بإيدينا (إضافات احترافية)
# ----------------------------------------------------------

def pause_until(target_hour, target_minute):
    """توقف الكود لحد ما الساعة توصل لوقت معين"""
    while True:
        now = time.localtime()
        if now.tm_hour == target_hour and now.tm_min == target_minute:
            break
        time.sleep(10)


def measure_execution_time(func, *args, **kwargs):
    """تحسب وقت تنفيذ أي دالة"""
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    print(f"⏱️ وقت التنفيذ: {end - start:.4f} ثانية")
    return result


def countdown(seconds):
    """عداد تنازلي"""
    for i in range(seconds, 0, -1):
        print(i)
        time.sleep(1)
    print("⏰ انتهى الوقت!")


def stopwatch():
    """ستوب ووتش بسيط"""
    input("⏯️ اضغط Enter للبدء...")
    start = time.time()
    input("⏹️ اضغط Enter للإيقاف...")
    end = time.time()
    print(f"⏰ المدة: {end - start:.2f} ثانية")


def delay_message(message, seconds):
    """تأخير طباعة رسالة"""
    time.sleep(seconds)
    print(message)


def wait_until_date(target_date: str):
    """ينتظر لحد تاريخ معين (بصيغة YYYY-MM-DD)"""
    target = datetime.datetime.strptime(target_date, "%Y-%m-%d")
    while datetime.datetime.now() < target:
        time.sleep(3600)
    print("📅 التاريخ المحدد وصل!")


def time_difference(date1: str, date2: str):
    """تحسب الفرق بين تاريخين بالأيام"""
    d1 = datetime.datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(date2, "%Y-%m-%d")
    return abs((d2 - d1).days)


def timer_with_callback(seconds, callback):
    """مؤقت يستدعي دالة بعد وقت معين"""
    print(f"⏳ سيتم تشغيل الدالة بعد {seconds} ثانية...")
    time.sleep(seconds)
    callback()


def save_log_time(filename="time_log.txt"):
    """يحفظ الوقت الحالي في ملف Log"""
    with open(filename, "a", encoding="utf-8") as f:
        f.write(time.ctime() + "\n")
    print(f"📝 تم حفظ الوقت الحالي في {filename}")


def show_system_uptime():
    """يعرض مدة تشغيل النظام (لينكس فقط)"""
    if os.name == "posix":
        with open("/proc/uptime", "r") as f:
            seconds = float(f.readline().split()[0])
        hours = seconds // 3600
        print(f"🖥️ مدة التشغيل: {hours:.2f} ساعة")
    else:
        print("❌ هذا الأمر متاح في أنظمة Linux فقط.")


def wait_for_input(message="⏸️ اضغط Enter للمتابعة..."):
    """يوقف الكود لحد ما المستخدم يضغط Enter"""
    input(message)


def repeat_every(interval, func, *args, **kwargs):
    """ينفذ دالة كل مدة زمنية معينة"""
    while True:
        func(*args, **kwargs)
        time.sleep(interval)


def real_clock(duration=10):
    """يعرض الساعة في الوقت الحقيقي"""
    for _ in range(duration):
        print(time.strftime("%H:%M:%S", time.localtime()), end="\r")
        time.sleep(1)
    print("\n⌛ انتهى عرض الساعة.")


def display_time_animation(seconds=5):
    """أنيميشن بسيط للوقت"""
    for i in range(seconds):
        print(f"🕒 {time.strftime('%H:%M:%S')}", end="\r")
        time.sleep(1)
    print("\n🎬 الانتهاء من الأنيميشن.")