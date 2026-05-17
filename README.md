# 🤖 DeskAI — Professional Voice Assistant

DeskAI is a modular, skill-based voice assistant for the desktop, built with Python. It listens to your voice commands and can perform a wide range of tasks — from sending WhatsApp messages to controlling system volume — all through a clean GUI or a lightweight CLI.

---

## ✨ Features

- 🎙️ **Voice Recognition** — Continuously listens and processes spoken commands
- 🖥️ **GUI + CLI Modes** — Run with a modern `customtkinter` interface or headlessly in the terminal
- 🧩 **Skill-Based Architecture** — Skills are auto-loaded at startup; no manual wiring required
- 📦 **Modular Core** — Clean separation between context, dispatcher, assistant logic, and UI
- 🔔 **System Notifications** — Desktop alerts via `plyer`
- 📱 **WhatsApp Integration** — Send messages using `pywhatkit`
- 🔊 **Volume Control** — Manage system audio via `pycaw`
- 📊 **System Monitoring** — CPU, memory, and process info via `psutil`
- 🔢 **Natural Language Numbers** — Understands spoken numbers like "set volume to fifty" via `word2number`
- 📝 **Persistent Logging** — Logs stored at `~/.deskai/deskai.log`

---

## 📁 Project Structure

```
DeskAI/
├── main.py              # Entry point; CLI and GUI launch logic
├── requirements.txt     # Python dependencies
├── core/
│   ├── assistant.py     # Main DeskAI assistant class
│   ├── context.py       # AssistantContext (config, state)
│   ├── dispatcher.py    # Command routing and handler registry
│   └── skill_loader.py  # Auto-loads skills from config
├── skills/              # Individual skill modules (auto-discovered)
├── ui/
│   └── gui.py           # customtkinter GUI window
├── utils/               # Shared utilities
├── config/              # Configuration files
├── tests/               # Test suite
└── build/               # PyInstaller build output
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- A working microphone
- Windows (recommended for full `pycaw` support)

### Installation

```bash
# Clone the repository
git clone https://github.com/siddhesh-wagh/DeskAI.git
cd DeskAI

# Install dependencies
pip install -r requirements.txt
```

### Running DeskAI

```bash
# Launch with GUI (default)
python main.py

# Launch in CLI mode (no GUI)
python main.py --cli

# Enable verbose debug logging
python main.py --debug

# List all available skills
python main.py --list-skills
```

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `customtkinter` | Modern GUI framework |
| `pywhatkit` | WhatsApp automation |
| `plyer` | Desktop notifications |
| `pycaw` | Windows audio/volume control |
| `psutil` | System resource monitoring |
| `word2number` | Convert spoken numbers to integers |

Install all at once:

```bash
pip install -r requirements.txt
```

---

## 🧩 Skills System

Skills are Python modules placed in the `skills/` directory. They are **automatically discovered and loaded** at startup — no manual registration needed.

To see all available skills:

```bash
python main.py --list-skills
```

To add a new skill, create a `.py` file in the `skills/` folder following the base skill interface. The skill loader will pick it up on the next run.

---

## 🏗️ Architecture Overview

```
Voice Input
    │
    ▼
AssistantContext  ←─── config, state, paths
    │
    ▼
Dispatcher  ←─── registered command handlers (from skills)
    │
    ▼
DeskAI Core  ←─── orchestrates listen → dispatch → respond loop
    │
    ├── GUI (customtkinter window)   [default]
    └── CLI (stdout)                 [--cli flag]
```

The `DeskAI` class accepts three callbacks (`on_response`, `on_command`, `on_listening`) which are wired up by the GUI or printed to stdout in CLI mode. This keeps the core logic completely UI-agnostic.

---

## 🛠️ Building a Standalone Executable

DeskAI includes a PyInstaller spec file for packaging:

```bash
pyinstaller main.spec
```

The output will be placed in the `dist/` directory.

---

## 🪵 Logs

Logs are written to:

```
~/.deskai/deskai.log
```

Use `--debug` flag for verbose output during development.

---

## 🤝 Contributing

Contributions are welcome! To add a new skill or improve existing functionality:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/my-skill`)
3. Add your skill in the `skills/` folder
4. Test it with `python main.py --list-skills` and `python main.py --debug`
5. Submit a pull request

---

## 👤 Author

**Siddhesh Wagh**
- GitHub: [@siddhesh-wagh](https://github.com/siddhesh-wagh)

---

## 📄 License

This project is open source. Feel free to use, modify, and distribute it.
