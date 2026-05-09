import sys
import tkinter as tk
from tkinter import messagebox, ttk

from audio_switch_common import CONFIG_FILENAME, get_app_dir, load_config, save_config

try:
    from pycaw.pycaw import AudioDeviceState, AudioUtilities
except ModuleNotFoundError as error:
    AudioDeviceState = None
    AudioUtilities = None
    MISSING_DEPENDENCY = error.name
else:
    MISSING_DEPENDENCY = None


def get_active_devices():
    if MISSING_DEPENDENCY:
        raise RuntimeError(
            f"Manca la libreria Python '{MISSING_DEPENDENCY}'. "
            "Installa le dipendenze e riapri il configuratore."
        )

    devices = []

    for device in AudioUtilities.GetAllDevices():
        try:
            if device.state != AudioDeviceState.Active:
                continue
            if not str(device.id).startswith("{0.0.0."):
                continue

            devices.append(
                {
                    "id": device.id,
                    "name": device.FriendlyName,
                }
            )
        except Exception:
            continue

    return sorted(devices, key=lambda item: item["name"].lower())


class AudioDeviceConfigApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Audio Switcher - Configurazione")
        self.resizable(False, False)

        self.devices = []
        self.device_by_label = {}

        self.device_1_var = tk.StringVar()
        self.device_2_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.create_widgets()
        self.refresh_devices()

    def create_widgets(self):
        container = ttk.Frame(self, padding=16)
        container.grid(row=0, column=0, sticky="nsew")

        ttk.Label(container, text="Dispositivo 1").grid(row=0, column=0, sticky="w")
        self.device_1_combo = ttk.Combobox(
            container,
            textvariable=self.device_1_var,
            width=58,
            state="readonly",
        )
        self.device_1_combo.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(4, 12))

        ttk.Label(container, text="Dispositivo 2").grid(row=2, column=0, sticky="w")
        self.device_2_combo = ttk.Combobox(
            container,
            textvariable=self.device_2_var,
            width=58,
            state="readonly",
        )
        self.device_2_combo.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(4, 14))

        ttk.Button(container, text="Aggiorna lista", command=self.refresh_devices).grid(
            row=4, column=0, sticky="w"
        )
        ttk.Button(
            container,
            text="Apri cartella installazione",
            command=self.open_install_folder,
        ).grid(row=4, column=1, sticky="e", padx=(12, 8))
        ttk.Button(container, text="Salva", command=self.handle_save).grid(
            row=4, column=2, sticky="e"
        )

        ttk.Label(container, textvariable=self.status_var, foreground="#555555").grid(
            row=5, column=0, columnspan=3, sticky="w", pady=(14, 0)
        )

        container.columnconfigure(1, weight=1)

    def refresh_devices(self):
        try:
            self.devices = get_active_devices()
        except Exception as error:
            messagebox.showerror("Errore", f"Non riesco a leggere i dispositivi audio:\n{error}")
            return

        labels = self.build_labels(self.devices)
        self.device_1_combo["values"] = labels
        self.device_2_combo["values"] = labels

        config = load_config()
        self.select_configured_device(self.device_1_var, config.get("device_1"), 0)
        self.select_configured_device(self.device_2_var, config.get("device_2"), 1)

        if labels:
            self.status_var.set(f"Trovati {len(labels)} dispositivi audio attivi.")
        else:
            self.status_var.set("Nessun dispositivo audio attivo trovato.")

    def build_labels(self, devices):
        labels = []
        name_count = {}
        self.device_by_label = {}

        for device in devices:
            name = device["name"]
            name_count[name] = name_count.get(name, 0) + 1
            label = name if name_count[name] == 1 else f"{name} ({name_count[name]})"
            labels.append(label)
            self.device_by_label[label] = device

        return labels

    def select_configured_device(self, variable, configured_device, fallback_index):
        label = self.find_device_label(configured_device)
        labels = list(self.device_1_combo["values"])

        if label:
            variable.set(label)
        elif len(labels) > fallback_index:
            variable.set(labels[fallback_index])
        else:
            variable.set("")

    def find_device_label(self, configured_device):
        if not configured_device:
            return None

        configured_id = configured_device.get("id")
        configured_name = configured_device.get("name", "").lower()

        for label, device in self.device_by_label.items():
            if configured_id and device["id"] == configured_id:
                return label

        for label, device in self.device_by_label.items():
            if configured_name and device["name"].lower() == configured_name:
                return label

        return None

    def handle_save(self):
        label_1 = self.device_1_var.get()
        label_2 = self.device_2_var.get()

        if not label_1 or not label_2:
            messagebox.showwarning("Manca un dispositivo", "Scegli entrambi i dispositivi audio.")
            return

        device_1 = self.device_by_label[label_1]
        device_2 = self.device_by_label[label_2]

        if device_1["id"] == device_2["id"]:
            messagebox.showwarning(
                "Dispositivi uguali",
                "Scegli due dispositivi diversi da alternare.",
            )
            return

        try:
            saved_path = save_config(
                {
                    "device_1": device_1,
                    "device_2": device_2,
                    "last_target_id": "",
                }
            )
        except Exception as error:
            messagebox.showerror("Errore", f"Non riesco a salvare la configurazione:\n{error}")
            return

        self.status_var.set(f"Configurazione salvata in {saved_path}.")
        messagebox.showinfo("Salvato", "I due dispositivi audio sono stati salvati.")

    def open_install_folder(self):
        try:
            install_dir = get_app_dir()
            if sys.platform.startswith("win"):
                import os

                os.startfile(install_dir)
            else:
                messagebox.showinfo("Cartella installazione", str(install_dir))
        except Exception as error:
            messagebox.showerror(
                "Errore",
                f"Non riesco ad aprire la cartella di installazione:\n{error}",
            )


if __name__ == "__main__":
    if MISSING_DEPENDENCY:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Dipendenza mancante",
            "Manca una libreria necessaria per leggere i dispositivi audio.\n\n"
            "Apri PowerShell ed esegui:\n"
            'C:/Python314/python.exe -m pip install -r "c:/Users/zitos/Desktop/File/Progetti/My Project/Cange Audio/requirements.txt"',
        )
        sys.exit(1)

    app = AudioDeviceConfigApp()
    app.mainloop()
