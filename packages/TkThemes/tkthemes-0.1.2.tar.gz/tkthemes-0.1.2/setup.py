from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="TkThemes",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[],
    description="Contains dictionary of custom themes used for creting GUIs with Tkinter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tirthraj Girawale",
    url="https://github.com/TirthrajSG/TkThemes",
    python_requires=">=3.7"
)
