from setuptools import setup, find_packages

setup(
    name="Super lux library",  # اسم المكتبة
    version="0.2.0",
    author="zeyad",
    description="an library have time, json, os and more librarys",
    packages=find_packages(),
    install_requires=[
        # هنا تحط المكتبات اللي مكتبتك بتعتمد عليها
        "requests",
        "pandas"
    ],
)