# Whisper GUI  
A modern, easy-to-use Windows desktop GUI for OpenAI Whisper, featuring drag-and-drop transcription, progress tracking, ffmpeg detection, and fully local processing. No data is ever uploaded—everything runs on your machine using the official Whisper model.

---

## ✨ Features

- Drag-and-drop audio & video
- Progress bar based on Whisper segment count  
- Auto-save TXT + SRT output
- Real-time transcription log
- ffmpeg detection with clear warnings
- One-click install (install.bat)
- One-click launch (app.bat)
- 100% local and privacy-friendly (no cloud, no API keys)

---

## 🚀 Quick Start (Windows)

### 1. Download or clone this repository

git clone https://github.com/2577manmeet/whisper-gui.git

### 2. Run the installer  
Double-click:

install.bat

This will:

- Create a Python virtual environment (.venv)
- Install all dependencies
- Prepare everything automatically

### 3. Launch the GUI  
Double-click:

app.bat

---

## 🎥 Usage

1. Drag a media file into the window or click “Choose file…”
2. Select a Whisper model  
3. Press Transcribe
4. View progress in real time  
5. Output files will appear in:

output/<filename>.txt  
output/<filename>.srt  

Supported formats include .mp3, .wav, .m4a, .mp4, .webm, .flac, .ogg, and anything ffmpeg can decode.

---


## 🛠 Requirements

- Windows 10 or 11  
- Python 3.10+  
- ffmpeg installed and in PATH  
  - Download: https://ffmpeg.org/download.html  
  - Or install via Chocolatey:  
    choco install ffmpeg

---

## 📦 Dependencies

Installed automatically via install.bat:

- openai-whisper
- customtkinter
- torch
- Additional Python utilities

---

## 🧠 About Whisper

This project uses the official OpenAI Whisper model.  
Repository:  
https://github.com/openai/whisper

Whisper is an open-source speech-to-text model trained on 680,000+ hours of multilingual audio.  
Massive thanks to OpenAI for releasing it under the MIT license.

---


## 📄 License

This project is released under the MIT License.

Whisper is MIT-licensed by OpenAI.  
See: https://github.com/openai/whisper/blob/main/LICENSE

---

## ⭐ Contributing

Issues, feature requests, and pull requests are welcome.

---

## 🎉 Enjoy fast, private, local transcription!

If this project helps you, consider giving the repository a ⭐ star!
