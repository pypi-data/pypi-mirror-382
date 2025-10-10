from setuptools import setup, find_packages

setup(
    name="lumivox",
    version="0.4.7",
    author="Arjun",
    author_email="",
    description="🎤 Offline voice-controlled LED system for students and robotics labs.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/lumivox/",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "vosk>=0.3.45",
        "sounddevice>=0.4.6",
        "pyserial>=3.5",
        "tk",
        "numpy>=1.24"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
