from setuptools import setup, find_packages
import os

# قراءة README.md
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "مكتبة Python لتنزيل مقاطع الفيديو من وسائل التواصل الاجتماعي"

def get_version():
    """الحصول على الإصدار من ملف __init__.py"""
    init_path = os.path.join(os.path.dirname(__file__), "jafrdow", "__init__.py")
    
    if not os.path.exists(init_path):
        return "0.1.0"
    
    try:
        with open(init_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    # استخراج القيمة بين علامتي الاقتباس
                    version = line.split("=")[1].strip()
                    # إزالة علامات الاقتباس
                    version = version.strip('"').strip("'")
                    return version
    except Exception:
        pass
    
    return "0.1.0"

setup(
    name="jafrdow",
    version=get_version(),
    author="Jafr",
    author_email="jafr@example.com",
    description="مكتبة Python لتنزيل مقاطع الفيديو من وسائل التواصل الاجتماعي",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jafr-dev/jafrdow",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet",
        "Topic :: Multimedia :: Video",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.1",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "jafrdow=jafrdow.cli:main",
        ],
    },
    keywords=[
        "download", 
        "video", 
        "social media", 
        "youtube", 
        "tiktok", 
        "instagram",
        "twitter",
        "facebook",
        "arabic"
    ],
)