from setuptools import setup, find_packages

setup(
    name="superLibrary",  # اسم المكتبة
    version="0.1.0",
    author="zeyad",
    description="an library have time, json, os and more librarys",
    packages=find_packages(),
    install_requires=[
        # هنا تحط المكتبات اللي مكتبتك بتعتمد عليها
        "requests",
        "pandas"
    ],
)