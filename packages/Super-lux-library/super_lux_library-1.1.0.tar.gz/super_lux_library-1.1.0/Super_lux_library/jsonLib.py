import json
import os


__all__ = [
    "dump_json",
    "dumps_json",
    "load_json",
    "loads_json",
    "json_encode",
    "json_decode",
    "get_json_path",
    "create_database",
    "read_json",
    "write_json",
    "save_json",
    "update_json",
    "delete_key",
    "append_to_json",
    "clear_json"
]


# ⚙️ أوامر مكتبة json الأصلية
def dump_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def dumps_json(data):
    return json.dumps(data, indent=4, ensure_ascii=False)


def load_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def loads_json(json_text):
    return json.loads(json_text)


def json_encode(obj):
    return json.dumps(obj, indent=4, ensure_ascii=False)


def json_decode(json_str):
    return json.loads(json_str)


# 🗂️ تحديد مسار ملف الـ database.json
def get_json_path():
    return os.path.join(os.getcwd(), "database.json")


# 🧱 إنشاء ملف قاعدة بيانات لو مش موجود
def create_database():
    path = get_json_path()
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)
        print("✅ تم إنشاء الملف database.json بنجاح!")
    else:
        print("📁 الملف database.json موجود بالفعل.")


# 📖 قراءة محتوى JSON
def read_json():
    path = get_json_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print("⚠️ الملف غير موجود، تم إنشاؤه تلقائيًا.")
        create_database()
        return {}


# ✍️ كتابة بيانات جديدة (استبدال كامل)
def write_json(data):
    path = get_json_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# 💾 حفظ البيانات (اختصار للكتابة)
def save_json(data):
    """دالة سريعة لحفظ البيانات في database.json"""
    write_json(data)
    print("💾 تم حفظ البيانات في الملف database.json بنجاح!")


# 🔄 تحديث مفتاح داخل JSON
def update_json(key, value):
    data = read_json()
    data[key] = value
    write_json(data)
    print(f"✅ تم تحديث المفتاح '{key}' بنجاح!")


# 🗑️ حذف مفتاح من JSON
def delete_key(key):
    data = read_json()
    if key in data:
        del data[key]
        write_json(data)
        print(f"🗑️ تم حذف المفتاح '{key}' بنجاح.")
    else:
        print(f"⚠️ المفتاح '{key}' غير موجود.")


# ➕ إضافة بيانات جديدة بدون حذف القديمة
def append_to_json(new_data: dict):
    data = read_json()
    data.update(new_data)
    write_json(data)
    print("✅ تم إضافة البيانات الجديدة بنجاح!")


# 🧹 مسح كل محتوى ملف JSON
def clear_json():
    write_json({})
    print("🧹 تم مسح جميع البيانات في database.json.")