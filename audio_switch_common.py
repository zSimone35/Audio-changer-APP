import json
import os
import sys
from pathlib import Path


APP_NAME = "Audio Switcher"
CONFIG_FILENAME = "audio_switch_config.json"
SWITCHER_ICON = "Audio-Setting-Icon.ico"
DEVICE_1_ICON = "icon_headphones.ico"
DEVICE_2_ICON = "icon_monitor.ico"
DEFAULT_DEVICE_1_NAME = "HEADPHONES (3- High Definition Audio Device)"
DEFAULT_DEVICE_2_NAME = "OMEN 27qs (NVIDIA High Definition Audio)"


def get_app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_config_dir():
    base_dir = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")

    if base_dir:
        return Path(base_dir) / APP_NAME

    return get_app_dir()


def get_config_path():
    return get_config_dir() / CONFIG_FILENAME


def get_legacy_config_path():
    return get_app_dir() / CONFIG_FILENAME


def get_writable_config_dir():
    for config_dir in (get_config_dir(), get_app_dir()):
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            test_path = config_dir / ".write-test"
            test_path.write_text("", encoding="utf-8")
            test_path.unlink(missing_ok=True)
            return config_dir
        except Exception:
            continue

    return get_app_dir()


def load_config():
    for config_path in (get_config_path(), get_legacy_config_path()):
        if not config_path.exists():
            continue

        try:
            with config_path.open("r", encoding="utf-8") as config_file:
                return json.load(config_file)
        except Exception:
            continue

    return {}


def save_config(config):
    config_dir = get_writable_config_dir()

    config_path = config_dir / CONFIG_FILENAME
    with config_path.open("w", encoding="utf-8") as config_file:
        json.dump(config, config_file, indent=2, ensure_ascii=False)

    return config_path


def update_config(**values):
    config = load_config()
    config.update(values)
    save_config(config)
    return config


def get_log_path():
    log_dir = get_writable_config_dir()
    return log_dir / "audio_switcher.log"


def write_log(message):
    try:
        with get_log_path().open("a", encoding="utf-8") as log_file:
            log_file.write(message.rstrip() + "\n")
    except Exception:
        pass
