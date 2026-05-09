import os
import shutil
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

import win32com.client


APP_DIR_NAME = "Audio Switcher"
FILES_TO_INSTALL = [
    "Audio Switcher.exe",
    "Audio Switcher Config.exe",
    "Audio-Setting-Icon.ico",
    "icon_headphones.ico",
    "icon_monitor.ico",
]


def get_bundle_dir():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent / "installer" / "payload"


def get_install_dir():
    return Path(os.environ["LOCALAPPDATA"]) / APP_DIR_NAME


def copy_files(bundle_dir, install_dir):
    install_dir.mkdir(parents=True, exist_ok=True)

    for file_name in FILES_TO_INSTALL:
        source = bundle_dir / file_name
        destination = install_dir / file_name

        if not source.exists():
            raise FileNotFoundError(f"File mancante nell'installer: {file_name}")

        shutil.copy2(source, destination)


def create_shortcut(shell, shortcut_path, target_path, working_dir, icon_path, description):
    shortcut = shell.CreateShortcut(str(shortcut_path))
    shortcut.TargetPath = str(target_path)
    shortcut.WorkingDirectory = str(working_dir)
    shortcut.IconLocation = str(icon_path)
    shortcut.Description = description
    shortcut.Save()


def create_shortcuts(install_dir):
    warnings = []
    shell = win32com.client.Dispatch("WScript.Shell")

    switcher_exe = install_dir / "Audio Switcher.exe"
    headphones_icon = install_dir / "icon_headphones.ico"

    shortcuts = [
        (
            install_dir / "Audio Switcher.lnk",
            switcher_exe,
            headphones_icon,
            "Cambia uscita audio",
        ),
    ]

    for shortcut_path, target_path, icon_path, description in shortcuts:
        try:
            create_shortcut(
                shell,
                shortcut_path,
                target_path,
                install_dir,
                icon_path,
                description,
            )
        except Exception as error:
            warnings.append(f"{shortcut_path.name}: {error}")

    return warnings


def open_configurator(install_dir):
    config_path = install_dir / "Audio Switcher Config.exe"
    os.startfile(config_path)


def main():
    root = tk.Tk()
    root.withdraw()

    if not messagebox.askyesno(
        "Audio Switcher Setup",
        "Vuoi installare Audio Switcher su questo PC?",
    ):
        return

    install_dir = get_install_dir()

    try:
        copy_files(get_bundle_dir(), install_dir)
        shortcut_warnings = create_shortcuts(install_dir)
        open_configurator(install_dir)
    except Exception as error:
        messagebox.showerror(
            "Installazione non riuscita",
            f"Non riesco a completare l'installazione:\n\n{error}",
        )
        return

    warning_text = ""
    if shortcut_warnings:
        warning_text = (
            "\n\nAlcuni collegamenti non sono stati creati, ma l'app e' installata:\n"
            + "\n".join(shortcut_warnings[:3])
        )

    messagebox.showinfo(
        "Installazione completata",
        "Audio Switcher e' stato installato.\n\n"
        "Si aprira' il configuratore per scegliere i due dispositivi audio."
        + warning_text,
    )


if __name__ == "__main__":
    main()
