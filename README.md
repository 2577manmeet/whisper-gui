# whisper-gui

Windows app for running [OpenAI Whisper](https://github.com/openai/whisper) locally. Drop in an audio/video file, pick a model, get `.txt` and `.srt` in `output/`. Nothing gets uploaded anywhere.

## setup

1. Clone this repo
2. Run `install.bat` (makes a venv and installs deps)
3. Run `app.bat`

You need Python 3.10+, Windows 10/11, and [ffmpeg](https://ffmpeg.org/download.html) on your PATH. Chocolatey works too: `choco install ffmpeg`

## usage

Drag a file onto the window or hit "Choose file…", pick a model, hit Transcribe. Works with whatever ffmpeg can read — mp3, wav, m4a, mp4, webm, flac, ogg, etc.

## deps

`install.bat` pulls in openai-whisper, customtkinter, torch, and the rest.

## license

MIT. Whisper itself is MIT from OpenAI.
