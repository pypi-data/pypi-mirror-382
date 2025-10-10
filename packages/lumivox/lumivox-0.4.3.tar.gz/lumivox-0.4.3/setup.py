from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="lumivox",
    version="0.4.3",
    author="Arjun",
    description="Offline voice-controlled LED system for students and robotics labs",
    packages=find_packages(),
    install_requires=["vosk", "sounddevice", "pyserial"],
    include_package_data=True,
    python_requires=">=3.8",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
