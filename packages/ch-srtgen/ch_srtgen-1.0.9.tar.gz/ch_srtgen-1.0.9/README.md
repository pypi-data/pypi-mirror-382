# Integrated SRT Subtitle Generator

A tool that uses Whisper speech recognition and OpenAI GPT to generate Korean SRT subtitles.

## ⚠️ Requirements (read first)

- Python >= 3.10
- OpenAI API key set to `OPENAI_API_KEY`
- FFmpeg installed and available on PATH (for transcription/whisper features)
- Optional: install extras for whisper/torch

### FFmpeg installation (per OS)

- Windows (one of)
  - Chocolatey: `choco install ffmpeg`
  - Scoop: `scoop install ffmpeg`
  - Winget: `winget install --id=Gyan.FFmpeg -e`
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt update && sudo apt install -y ffmpeg`
- Fedora: `sudo dnf install -y ffmpeg`
- Arch: `sudo pacman -S ffmpeg`

Verify: `ffmpeg -version` should print version info.

## 🚀 Features

- **Integrated workflow**: Speech-to-text → Korean translation → SRT generation
- **Flexible execution**: Run full process or individual steps
- **User-friendly GUI**: Intuitive interface
- **Simplified structure**: Minimal dependencies

## 📁 Project Structure

```
SRT_Generator/
├── src/                           # Integrated GUI
│   ├── integrated_srt_generator.py
│   ├── requirements.txt
│   └── run_integrated.bat
├── translator/                    # Translation tools
│   └── src/local_whisper_korean_subtitle_generator/
│       └── tools/
│           ├── korean_translation_tool.py
│           └── srt_formatter_tool.py
├── input/                         # Input files
├── output/                        # Output files
└── README.md
```

## 🛠️ Installation and Run

### 빠른 설치 (모든 기능 포함)

#### 방법 1: pip install로 설치
```bash
# 기본 설치 (whisper 포함)
pip install ch_srtgen

# 또는 개발 모드로 설치
pip install -e .

# 개발용 도구 포함
pip install -e .[dev]
```

#### 방법 1-1: Python 스크립트로 자동 설치
```bash
python quick_install.py
```

#### 방법 2: 설치 스크립트 사용
```bash
# Windows
install_all.bat

# Linux/macOS
./install_all.sh
```


### Install from PyPI (자동 종속성 설치 포함)
```bash
pip install ch-srtgen
```

**🎯 설치 완료 메시지:**
```
============================================================
🎯 SRT Generator 설치 완료!
============================================================

✅ 모든 종속성이 설치되었습니다!
🎉 SRT Generator를 바로 사용할 수 있습니다.

📖 사용법:
  ch-srtgen-gui    # GUI 실행
  ch-srtgen        # CLI 실행

📁 프로젝트 구조:
  input/     - 입력 파일 (비디오/오디오)
  output/    - 출력 파일 (SRT 자막)
```

### 1. Run the integrated GUI (recommended)
```bash
ch-srtgen-gui
```

### 2. Run CLI
```bash
# Help
ch-srtgen --help

# Process video file
ch-srtgen input.mp4
```

## 📋 Usage

### Using the integrated GUI

1. **Settings**
   - Select Whisper model (tiny ~ large-v3)
   - Select language (auto, ko, en, ja, etc.)
   - Enter OpenAI API key

2. **File selection**
   - Input file: target video/audio file
   - Output folder: where to save result files

3. **Actions**
   - **Start full process**: Transcription → Translation → SRT generation
   - **Transcription only**: Generate JSON file
   - **Translation only**: Convert existing JSON to Korean SRT

### Workflow

1. **Transcription** (Whisper)
   - Video/Audio → JSON (timestamp + text)

2. **Korean translation** (OpenAI GPT)
   - English text → Korean translation

3. **SRT generation** (Formatter)
   - Translated text → SRT subtitle file

## 🔧 Configuration

### API key setup

#### Method 1: Environment file (.env) [recommended]
1. Copy `env.template` to `.env`
2. Put your real API key in `.env`:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

#### Method 2: Enter via GUI
- Enter the API key in the GUI after launching the app

#### Method 3: System environment variable
```bash
# Windows
set OPENAI_API_KEY=your_actual_api_key_here

# Linux/Mac
export OPENAI_API_KEY=your_actual_api_key_here
```

**⚠️ Security notes:**
- Never commit `.env` to Git
- Do not hardcode API keys in code
- Do not upload API keys to public repos

### Model selection
- **tiny**: Fastest, lower accuracy
- **base**: Balanced (recommended)
- **small**: Good accuracy
- **medium**: Higher accuracy
- **large**: Highest accuracy, slowest

## 📝 Output files

- **JSON file**: `filename.json` (Whisper result)
- **SRT file**: `filename.srt` (final subtitles)

## 🐛 Troubleshooting

### Common issues
1. **FFmpeg error**: Install FFmpeg
2. **API key error**: Check OpenAI API key
3. **Out of memory**: Use a smaller Whisper model

### Logs
You can check detailed progress and errors in the GUI log panel.

## 📄 License

This project is distributed under the MIT License.
