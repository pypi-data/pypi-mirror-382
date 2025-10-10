import sys
from setuptools import setup, find_packages
from pathlib import Path
import platform
import os

# Safely load README
readme_path = Path(__file__).parent / "README.md"
long_description = (
    readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
)

# Detect platform
current_platform = platform.system()
is_android = (
    sys.platform.startswith("linux") and "ANDROID_ROOT" in os.environ
)  # Termux detection

# Core dependencies (CLI + non-GUI)
install_requires = [
    "certifi>=2025.10.5",
    "charset-normalizer>=3.4.3",
    "colorama>=0.4.6",
    "idna>=3.10",
    "loguru>=0.7.3",
    "lz4>=4.4.4",
    "markdown-it-py>=4.0.0",
    "mdurl>=0.1.2",
    "packaging>=25.0",
    "protobuf>=6.32.1",
    "Pygments>=2.19.2",
    "requests>=2.32.5",
    "rich>=14.1.0",
    "urllib3>=2.5.0",
    "zstandard>=0.25.0",
    "python-magic>=0.4.27",
]
setup(
    name="HoyoSophonDL",
    version="1.0.4",
    author="Mr.Jo0x01",
    author_email="",
    description=(
        "HoyoSophonDL CLI is a Python-based reimplementation of HoYoPlay’s downloader logic. "
        "It allows users to list, validate, and download game assets directly from HoYoPlay manifests, "
        "with support for multi-threading, resumable downloads, and optional GUI mode."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jo0X01/HoyoSophonDL",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    extras_require={
        "gui": [
            "PyQt6>=6.9.1",
            "PyQt6-Qt6>=6.9.2",
            "PyQt6_sip>=13.10.2",
        ]
    },
    entry_points={
        "console_scripts": [
            "hs_dl = HoyoSophonDL.__main__:main",
            "hs-dl = HoyoSophonDL.__main__:main",
            "sophon-dl = HoyoSophonDL.__main__:main",
            "hoyosophon_dl = HoyoSophonDL.__main__:main",
            "HoyoSophonDL = HoyoSophonDL.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.9",
)
