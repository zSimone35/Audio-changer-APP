import comtypes
from comtypes import GUID, COMMETHOD, HRESULT
from comtypes.client import CreateObject
import ctypes
from pycaw.pycaw import AudioUtilities, AudioDeviceState
import os
import sys
from pathlib import Path
import win32com.client

from audio_switch_common import (
    DEFAULT_DEVICE_1_NAME,
    DEFAULT_DEVICE_2_NAME,
    DEVICE_1_ICON,
    DEVICE_2_ICON,
    SWITCHER_ICON,
    get_app_dir,
    load_config,
    update_config,
    write_log,
)


def is_playback_device(device):
    return str(device.id).startswith("{0.0.0.")


def resolve_device_id(devices, configured_device, fallback_name):
    configured_id = configured_device.get("id") if configured_device else None
    configured_name = configured_device.get("name", "") if configured_device else ""
    configured_name = configured_name.lower()
    fallback_name = fallback_name.lower()

    for device in devices:
        try:
            if (
                device.state == AudioDeviceState.Active
                and is_playback_device(device)
                and configured_id
                and device.id == configured_id
            ):
                return device.id
        except Exception:
            continue

    for device in devices:
        try:
            if device.state != AudioDeviceState.Active or not is_playback_device(device):
                continue

            device_name = device.FriendlyName.lower()
            if configured_name and device_name == configured_name:
                return device.id
            if fallback_name and fallback_name in device_name:
                return device.id
        except Exception:
            continue

    return None

# Function to create the PolicyConfig client with a specific IID
def get_policy_config_client(clsid_str, iid_str):
    class IPolicyConfig(comtypes.IUnknown):
        _iid_ = GUID(iid_str)
        _methods_ = [
            COMMETHOD([], HRESULT, 'GetMixFormat',
                      (['in'], ctypes.c_void_p, 'pDevice'),
                      (['out'], ctypes.POINTER(ctypes.c_void_p), 'ppFormat')),
            COMMETHOD([], HRESULT, 'GetDeviceFormat',
                      (['in'], ctypes.c_void_p, 'pDevice'),
                      (['in'], ctypes.c_int, 'bDefault'),
                      (['out'], ctypes.POINTER(ctypes.c_void_p), 'ppFormat')),
            COMMETHOD([], HRESULT, 'ResetDeviceFormat',
                      (['in'], ctypes.c_void_p, 'pDevice')),
            COMMETHOD([], HRESULT, 'SetDeviceFormat',
                      (['in'], ctypes.c_void_p, 'pDevice'),
                      (['in'], ctypes.c_void_p, 'pEndpointFormat'),
                      (['in'], ctypes.c_void_p, 'pMixFormat')),
            COMMETHOD([], HRESULT, 'GetProcessingPeriod',
                      (['in'], ctypes.c_void_p, 'pDevice'),
                      (['in'], ctypes.c_int, 'bDefault'),
                      (['out'], ctypes.POINTER(ctypes.c_longlong), 'pmftDefaultPeriod'),
                      (['out'], ctypes.POINTER(ctypes.c_longlong), 'pmftMinimumPeriod')),
            COMMETHOD([], HRESULT, 'SetProcessingPeriod',
                      (['in'], ctypes.c_void_p, 'pDevice'),
                      (['in'], ctypes.POINTER(ctypes.c_longlong), 'pmftPeriod')),
            COMMETHOD([], HRESULT, 'GetShareMode',
                      (['in'], ctypes.c_void_p, 'pDevice'),
                      (['out'], ctypes.POINTER(ctypes.c_void_p), 'pMode')),
            COMMETHOD([], HRESULT, 'SetShareMode',
                      (['in'], ctypes.c_void_p, 'pDevice'),
                      (['in'], ctypes.c_void_p, 'mode')),
            COMMETHOD([], HRESULT, 'GetPropertyValue',
                      (['in'], ctypes.c_void_p, 'pDevice'),
                      (['in'], ctypes.c_void_p, 'key'),
                      (['out'], ctypes.POINTER(ctypes.c_void_p), 'value')),
            COMMETHOD([], HRESULT, 'SetPropertyValue',
                      (['in'], ctypes.c_void_p, 'pDevice'),
                      (['in'], ctypes.c_void_p, 'key'),
                      (['in'], ctypes.c_void_p, 'value')),
            COMMETHOD([], HRESULT, 'SetDefaultEndpoint',
                      (['in'], ctypes.c_wchar_p, 'wszDeviceId'),
                      (['in'], ctypes.c_int, 'eRole')),
            COMMETHOD([], HRESULT, 'SetEndpointVisibility',
                      (['in'], ctypes.c_wchar_p, 'wszDeviceId'),
                      (['in'], ctypes.c_int, 'fVisible')),
        ]
    
    return CreateObject(GUID(clsid_str), interface=IPolicyConfig)

def set_default_device(device_id):
    # CLSID for PolicyConfigClient
    clsid = '{870af99c-171d-4f9e-af0d-e63df40c2bc9}'
    
    # List of IIDs to try (Newer Windows versions often use the second one)
    iids = [
        '{F8679F50-850A-41CF-9C72-430F290290C8}', # Win 10 (newer) / Win 11
        '{870af99c-171d-4f9e-af0d-e63df40c2bc9}', # Win 10 (older)
        '{25388c96-23e5-4508-a662-7f6609c61e8e}',
        '{294935CE-F637-4E7C-A41B-2139141F185F}'
    ]
    
    success = False
    last_error = None
    
    for iid_str in iids:
        try:
            policy_config = get_policy_config_client(clsid, iid_str)
            policy_config.SetDefaultEndpoint(device_id, 0) # Console
            policy_config.SetDefaultEndpoint(device_id, 1) # Multimedia
            policy_config.SetDefaultEndpoint(device_id, 2) # Communications
            success = True
            break
        except Exception as e:
            last_error = e
            continue
            
    if not success:
        raise last_error

def update_shortcut_icon(icon_name):
    icon_path = get_app_dir() / icon_name
    if not icon_path.exists():
        icon_path = get_app_dir() / SWITCHER_ICON

    updated = False
    
    try:
        shell = win32com.client.Dispatch("WScript.Shell")

        paths_to_check = [
            get_app_dir() / "Audio Switcher.lnk",
            Path(shell.SpecialFolders("Programs")) / "Audio Switcher" / "Audio Switcher.lnk",
            Path(shell.SpecialFolders("Programs")) / "Audio Switcher.lnk",
            Path(os.environ.get("APPDATA", ""))
            / "Microsoft"
            / "Internet Explorer"
            / "Quick Launch"
            / "User Pinned"
            / "TaskBar"
            / "Audio Switcher.lnk",
        ]

        for link_path in paths_to_check:
            if link_path.exists():
                try:
                    shortcut = shell.CreateShortcut(str(link_path))
                    shortcut.IconLocation = str(icon_path)
                    shortcut.Save()
                    try:
                        link_path.touch()
                    except:
                        pass
                    updated = True
                except Exception:
                    continue
        
        if updated:
            # SHCNE_ASSOCCHANGED = 0x08000000, SHCNF_IDLIST = 0x0000
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
            
    except Exception:
        pass


def get_current_device():
    try:
        return AudioUtilities.GetSpeakers()
    except Exception:
        return None


def choose_target(current_id, target_1_id, target_2_id, last_target_id):
    if target_1_id and current_id == target_1_id:
        return target_2_id, DEVICE_2_ICON
    if target_2_id and current_id == target_2_id:
        return target_1_id, DEVICE_1_ICON
    if target_1_id and target_2_id and last_target_id == target_1_id:
        return target_2_id, DEVICE_2_ICON
    if target_1_id:
        return target_1_id, DEVICE_1_ICON
    if target_2_id:
        return target_2_id, DEVICE_2_ICON
    return None, None


def show_error(message):
    ctypes.windll.user32.MessageBoxW(0, message, "Audio Switcher", 0x10)

def main():
    config = load_config()
    devices = AudioUtilities.GetAllDevices()
    
    target_1_id = resolve_device_id(
        devices,
        config.get("device_1"),
        DEFAULT_DEVICE_1_NAME,
    )
    target_2_id = resolve_device_id(
        devices,
        config.get("device_2"),
        DEFAULT_DEVICE_2_NAME,
    )
            
    if not target_1_id and not target_2_id:
        show_error(
            "Non trovo i dispositivi audio configurati.\n\n"
            "Apri Audio Switcher Config e scegli due uscite audio attive."
        )
        return

    current_device = get_current_device()
    current_id = current_device.id if current_device else None
    new_device_id, new_icon = choose_target(
        current_id,
        target_1_id,
        target_2_id,
        config.get("last_target_id"),
    )

    if new_device_id:
        try:
            set_default_device(new_device_id)
            try:
                update_config(last_target_id=new_device_id)
            except Exception as state_error:
                write_log(f"Non riesco a salvare lo stato ultimo target: {state_error}")
            if new_icon:
                update_shortcut_icon(new_icon)
        except Exception as e:
            write_log(f"Errore cambio dispositivo: {e}")
            show_error(f"Errore durante il cambio dispositivo:\n{e}")

if __name__ == "__main__":
    main()
