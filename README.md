# 🎧 Windows Audio Switcher

**Windows Audio Switcher** is a lightweight and instant utility for Windows that allows you to toggle the default audio playback device between two selected outputs (e.g., Speakers and Headphones) with a single click.

![Platform](https://img.shields.io/badge/platform-Windows-0078d7.svg)

## ✨ Key Features

- **One-Click Toggle**: Instantly switch between two pre-configured audio devices.
- **Silent Execution**: The switcher runs in the background without opening any intrusive windows.
- **Visual Feedback**: The shortcut icon updates dynamically to show which device is currently active.
- **Simple Configuration**: Includes an intuitive graphical tool to choose your preferred devices.
- **FxSound Compatible**: Works perfectly even if you use FxSound as an intermediate audio layer.

## 🚀 Getting Started

### Installation
1. Download and run the `Audio Switcher Setup.exe` file.
2. Follow the installer instructions to complete the installation on your PC.

### Configuration
At first launch, or whenever you want to change your devices:
1. Open the **Audio Switcher Configurator** from the Start menu or the installation folder.
2. Select the two audio devices you want to toggle from the dropdown menus.
3. Click **Save**.

### Usage
- Click the **Audio Switcher** shortcut (which you can pin to your taskbar or desktop).
- With each click, the system will switch from one device to the other, and the icon will change to reflect the current selection.

## ⚙️ Technical Details

The application interacts directly with the **Windows Multimedia Device (MMDevice)** APIs to ensure a fast and reliable switch without needing to restart any running audio applications.

The configuration is saved locally at:
```text
%LOCALAPPDATA%\Audio Switcher\audio_switch_config.json
```

---
*Developed to make audio management on Windows simpler and faster.*
