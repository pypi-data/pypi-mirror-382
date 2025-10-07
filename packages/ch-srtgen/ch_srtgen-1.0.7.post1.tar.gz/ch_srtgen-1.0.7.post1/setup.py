from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements.txt
def read_requirements():
    requirements = []
    if os.path.exists("src/requirements.txt"):
        with open("src/requirements.txt", "r", encoding="utf-8") as fh:
            requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return requirements

setup(
    name="ch_srtgen",
    version="1.0.7.post1",
    author="SRT Generator Team",
    author_email="srt-generator@example.com",
    description="AI-powered SRT subtitle generator with Whisper and OpenAI translation",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/srt-generator",
    packages=find_packages(where="translator/src", exclude=["tests", "tests.*", "*tests*", "*__pycache__*"]),
    package_dir={"": "translator/src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.10",
    # 경량 기본 의존성만 포함 (대용량/플랫폼 의존 패키지는 extras로 분리)
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
        "crewai>=0.28.0",
    ],
    extras_require={
        # 음성 인식/미디어 관련 무거운 패키지는 선택 설치
        "whisper": [
            "openai-whisper",
            "torch>=2.0.0",
            "torchaudio>=2.0.0",
            "ffmpeg-python>=0.2.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="whisper, openai, translation, subtitle, srt, ai, speech-to-text",
    project_urls={
        "Bug Reports": "https://github.com/your-username/srt-generator/issues",
        "Source": "https://github.com/your-username/srt-generator",
        "Documentation": "https://github.com/your-username/srt-generator#readme",
    },
    entry_points={
        "console_scripts": [
            "srt-generator=srt_generator.cli:main",
            "srt-generator-gui=srt_generator.gui_app:main",
        ],
    },
)
