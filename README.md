<div align="center">
  <h1>🔍 AI Session Mapper</h1>
  <p><strong>Never lose an AI coding session again.</strong></p>
  <p>A lightning-fast, dependency-free CLI tool to hunt down, decode, and map your invisible AI coding sessions (Gemini CLI & Opencode) into human-readable paths.</p>
  
  [![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
  
  [Tiếng Việt](README_vi.md) • [English](README.md)
</div>

---

## 🎯 The Pain Point

When you use local AI developer tools like **Gemini CLI** or **Opencode**, they track your workspace sessions—but they hide this data deep inside your OS AppData, often applying base64 encoding or strange path obfuscation. 

*Tried to find that awesome prototype you generated 3 days ago but forgot where it was saved?*

**AI Session Mapper** solves this! It digs into the guts of `~/.gemini` and `%APPDATA%\ai.opencode.desktop`, decrypts the obfuscated paths, and perfectly structures everything into a single, elegant terminal dashboard.

## ✨ Features

- **No 3rd-Party Dependencies**: Written in pure standard Python. Just download and run.
- **Opencode Decryptor**: Parses `opencode.global.dat` instead of relying on obfuscated `.dat` filenames to retrieve the perfect, absolute paths to your workspaces.
- **Gemini Tracker**: Automatically parses dictionary logic inside `projects.json` mapping.
- **Unified Overview**: Shows the tool used, parsed session names, exact filesystem paths, and last active timestamps.
- **Cross-Platform Compatibility**: Automatically normalizes file paths and handles Windows default OS encoding seamlessly without emoji crash bugs.

## 🚀 Usage

### Method 1: Run with Python

```cmd
cd cli
python session_mapper.py
```

### Method 2: Compile to a Standalone Executable (Windows)

You can easily compile this into a single, portable `.exe` file using `PyInstaller`. This way, you don't even need Python installed to run it!

1. Install PyInstaller:
   ```cmd
   pip install pyinstaller
   ```
2. Compile into a single file:
   ```cmd
   pyinstaller --onefile --name last_session session_mapper.py
   ```
3. Your executable will be ready at:
   ```cmd
   dist/last_session.exe
   ```
You can copy this `last_session.exe` anywhere (like `C:\Users\YourName\AppData\Local\OpenCode`) and run it simply by double-clicking it or typing `last_session` in terminal.

## 📊 Example Output

```text
[i] Scanning for AI Agent Logging Sessions (Gemini & Opencode)...
-----------------------------------------------------------------------------------------------------
| Agent      | Session Name       | Project Directory                                | Last Active  |
-----------------------------------------------------------------------------------------------------
| Gemini     | nextjs-dashboard   | /Users/dev/workspace/nextjs-dashboard            | Unknown      |
| Gemini     | ai-session-mapper  | /Users/dev/workspace/ai-session-mapper           | 10m ago      |
| Opencode   | awesome-app        | C:\Projects\awesome-app                          | 1d ago       |
| Opencode   | data-analyzer      | C:\Projects\data-analyzer                        | 1h ago       |
-----------------------------------------------------------------------------------------------------
```

## 🛠 How it Works

- **Gemini CLI:** Looks for mappings in `~/.gemini/projects.json` and syncs up folder modification times in `~/.gemini/sessions/`.
- **Opencode:** Reaches into `%APPDATA%/ai.opencode.desktop/opencode.global.dat` to extract internal `globalSync.project` JSON structures, bypassing base64-shortened file dumps entirely for 100% path accuracy.

## 📄 License

MIT License. Feel free to fork and map more CLI tools!
