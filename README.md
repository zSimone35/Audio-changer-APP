# 🎧 Windows Audio Switcher

**Windows Audio Switcher** is a lightweight and instant utility for Windows that allows you to toggle the default audio playback device between two selected outputs (e.g., Speakers and Headphones) with a single click.

[![Download](https://img.shields.io/github/v/release/zSimone35/Audio-changer-APP?label=Download&color=blue)](https://github.com/zSimone35/Audio-changer-APP/releases/latest)
![Platform](https://img.shields.io/badge/platform-Windows-0078d7.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Key Features

- **One-Click Toggle**: Instantly switch between two pre-configured audio devices.
- **Silent Execution**: The switcher runs in the background without opening any intrusive windows.
- **Visual Feedback**: The shortcut icon updates dynamically to show which device is currently active.
- **Simple Configuration**: Includes an intuitive graphical tool to choose your preferred devices.
- **FxSound Compatible**: Works perfectly even if you use FxSound as an intermediate audio layer.

## 🚀 Getting Started

### Installation
1. Download the latest release using the badge above, or go to the [Releases page](https://github.com/zSimone35/Audio-changer-APP/releases/latest).
2. Run the `Audio Switcher Setup.exe` file and follow the installer instructions.

### Configuration
At first launch, or whenever you want to change your devices:
1. Open the **Audio Switcher Configurator** from the Start menu or the installation folder.
2. Select the two audio devices you want to toggle from the dropdown menus.
3. Click **Save**.

### Usage
- Click the **Audio Switcher** shortcut (which you can pin to your taskbar or desktop).
- With each click, the system will switch from one device to the other, and the icon will change to reflect the current selection.

## 🛠️ Build from Source

If you want to run the app directly from source instead of using the installer:

### Requirements
- Python 3.10+
- Install dependencies:
  ```
  pip install -r requirements.txt
  ```

### Run
- **Switcher** (no console window): `pythonw audio_switch.pyw`
- **Configurator** (GUI): `python audio_device_config.py`

## ⚙️ Technical Details

The application interacts directly with the **Windows Multimedia Device (MMDevice)** APIs to ensure a fast and reliable switch without needing to restart any running audio applications.

The configuration is saved locally at:
```text
%LOCALAPPDATA%\Audio Switcher\audio_switch_config.json
```

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---
*Developed to make audio management on Windows simpler and faster.*
