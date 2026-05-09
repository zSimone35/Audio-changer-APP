# Audio Switcher

Audio Switcher is a small Windows utility that toggles the default playback device between two user-selected audio outputs.

The project includes:

- `audio_switch.pyw`: silent one-click audio output switcher.
- `audio_device_config.py`: small graphical configurator for choosing the two devices.
- `setup_audio_switcher.py`: installer wrapper used to create the distributable setup executable.
- `build_installer.ps1`: build script that creates the two app executables, the setup executable, and the release zip.

## Requirements

- Windows 10 or Windows 11
- Python 3.11+ for development
- Dependencies from `requirements.txt`

End users do not need Python when using the generated installer.

## Run From Source

```powershell
python -m pip install -r requirements.txt
python audio_device_config.py
python audio_switch.pyw
```

The configurator stores the selected devices in:

```text
%LOCALAPPDATA%\Audio Switcher\audio_switch_config.json
```

## Build Installer

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_installer.ps1
```

The final files are created in:

```text
release\
```

Share `release\Audio Switcher Installer.zip` or `release\Audio Switcher Setup.exe`.

The installer places the application and its shortcuts in:

```text
%LOCALAPPDATA%\Audio Switcher
```

Pin `%LOCALAPPDATA%\Audio Switcher\Audio Switcher.lnk` to the Windows taskbar if you want the dynamic shortcut icon behavior. The configurator can open this folder for you after installation.

## FxSound Note

If FxSound is running, it can remain the Windows default playback device while adapting to the selected physical output. Audio Switcher keeps the original one-click behavior: switch endpoint, update the shortcut icon, and exit.
