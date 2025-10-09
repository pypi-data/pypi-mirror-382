from setuptools import setup, find_packages

setup(
    name="lumivox",
    version="0.3.0",
    author="Arjun",
    description="Offline voice-controlled RGB LED system using Vosk for STEM learning. Automatically downloads the Indian-English model.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["vosk", "sounddevice", "pyserial", "requests"],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "lumivox-demo = lumivox.demo:run_demo"
        ]
    },
)
