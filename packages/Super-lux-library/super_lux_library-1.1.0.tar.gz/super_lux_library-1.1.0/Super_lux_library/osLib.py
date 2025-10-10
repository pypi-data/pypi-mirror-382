import os


__all__ = [
    "get_system_name",
    "get_system_info",
    "get_current_dir",
    "change_dir",
    "list_dir",
    "path_exists",
    "join_path",
    "get_basename",
    "get_dirname",
    "split_path",
    "make_dir",
    "make_dirs",
    "remove_dir",
    "remove_dirs",
    "delete_file",
    "rename_file",
    "get_file_size",
    "get_env",
    "get_env_var",
    "set_env_var",
    "run_command",
    "is_absolute",
    "get_absolute_path",
    "is_file",
    "is_dir"
]


# 🧩 معلومات النظام
def get_system_name():
    return os.name


def get_system_info():
    return os.uname()


# 📂 المسارات
def get_current_dir():
    return os.getcwd()


def change_dir(path):
    os.chdir(path)


def list_dir(path="."):
    return os.listdir(path)


def path_exists(path):
    return os.path.exists(path)


def join_path(folder, file):
    return os.path.join(folder, file)


def get_basename(path):
    return os.path.basename(path)


def get_dirname(path):
    return os.path.dirname(path)


def split_path(path):
    return os.path.split(path)


# 📁 إنشاء أو حذف المجلدات
def make_dir(folder):
    os.mkdir(folder)


def make_dirs(path):
    os.makedirs(path)


def remove_dir(folder):
    os.rmdir(folder)


def remove_dirs(path):
    os.removedirs(path)


# 📄 التعامل مع الملفات
def delete_file(file):
    os.remove(file)


def rename_file(old, new):
    os.rename(old, new)


def get_file_size(file):
    return os.path.getsize(file)


# ⚙️ متغيرات البيئة
def get_env():
    return os.environ


def get_env_var(var_name):
    return os.environ.get(var_name)


def set_env_var(key, value):
    os.environ[key] = value


# 🚀 تشغيل أوامر النظام
def run_command(command):
    return os.system(command)


# 💾 التعامل مع المسارات
def is_absolute(path):
    return os.path.isabs(path)


def get_absolute_path(path):
    return os.path.abspath(path)


def is_file(path):
    return os.path.isfile(path)


def is_dir(path):
    return os.path.isdir(path)