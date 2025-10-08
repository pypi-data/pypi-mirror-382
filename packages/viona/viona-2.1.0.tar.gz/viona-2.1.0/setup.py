from setuptools import setup, find_packages
from pathlib import Path

readme = Path(__file__).parent / "README.md"
long_description = readme.read_text(encoding="utf-8") if readme.exists() else "Viona AI - Orvix Games Python API istemcisi."

setup(
    name="viona",
    version="2.1.0",
    author="Orvix Games",
    author_email="destek@orvixgames.com",
    description="Viona AI modeline erişim sağlayan hızlı, güvenli ve asenkron destekli Python API istemcisi.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://viona.orvixgames.com/app/modul/viona-api-modul.php",
    license="MIT",
    packages=find_packages(exclude=("tests", "examples", "build", "dist", "venv", "__pycache__")),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "requests>=2.25.1",
        "aiohttp>=3.8.1",
        "httpx>=0.23.0",
        "tqdm>=4.65.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "viona=viona.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: Turkish",
    ],
    keywords="viona ai api orvixgames yapayzeka client python modul",
    project_urls={
        "Documentation": "https://viona.orvixgames.com/app/modul/viona-api-modul.php",
        "Homepage": "https://viona.orvixgames.com/app/modul/viona-api-modul.php",
    },
)
