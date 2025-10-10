import sys
import os
import time
import threading
import subprocess

try:
    import keyboard
    import pyperclip
    import requests
except ImportError:
    # This will only print if run directly, not in the background process.
    print("AshClip ERROR: Required libraries not found.")
    print("Please run: pip install keyboard pyperclip requests")
    sys.exit(1)

# --- Configuration ---
BASE_URL = "https://cmd.pythonanywhere.com"

# --- State Variable ---
script_running = True

def set_clipboard_feedback(message):
    """Safely sets the clipboard with a status message."""
    try:
        pyperclip.copy(message)
    except Exception:
        # Fails silently if clipboard is unavailable.
        pass

def fetch_content():
    """
    Core function triggered by the hotkey. Fetches file content from Nexus Hub
    and provides feedback via the clipboard.
    """
    try:
        time.sleep(0.1) # Allow clipboard to update after user's copy action.
        clipboard_content = pyperclip.paste().strip()

        if not clipboard_content:
            set_clipboard_feedback("AshClip Error: Clipboard is empty. Please copy a filename first.")
            return

        parts = clipboard_content.split('/')
        url = ""

        if len(parts) == 2 and parts[0].isdigit() and len(parts[0]) == 4:
            # Private file format: "1234/filename.txt"
            code, filename = parts[0], parts[1]
            url = f"{BASE_URL}/private_download_specific/{code}/{filename}"
        else:
            # Public file format: "filename.txt"
            filename = clipboard_content
            url = f"{BASE_URL}/get/{filename}"

        response = requests.get(url, timeout=10)
        
        if response.status_code == 404:
            set_clipboard_feedback(f"AshClip Error: File '{filename}' not found or has expired.")
            return
            
        # Raise an exception for other bad status codes (like 500).
        response.raise_for_status()

        file_content = response.text
        pyperclip.copy(file_content)
        # The success feedback is the content itself. No extra message needed.

    except requests.exceptions.RequestException:
        set_clipboard_feedback("AshClip Error: Network issue. Could not connect to Nexus Hub.")
    except Exception:
        set_clipboard_feedback("AshClip Error: An unexpected error occurred.")

def stop_script():
    """
    Triggered by the kill switch hotkey to gracefully stop the script.
    """
    global script_running
    script_running = False
    keyboard.unhook_all()

def run_hotkey_listener():
    """
    The main logic that runs in the background, listening for hotkeys.
    """
    global script_running
    
    # Use a thread for the fetch function to keep the listener responsive.
    keyboard.add_hotkey('ctrl+shift+a', lambda: threading.Thread(target=fetch_content).start())
    keyboard.add_hotkey('ctrl+z', stop_script)

    while script_running:
        time.sleep(1)

def main():
    """
    Main entry point. Determines whether to start the background process
    or to run the listener directly.
    """
    # If run with '--background', start the listener. This is for the detached process.
    if '--background' in sys.argv:
        try:
            run_hotkey_listener()
        except Exception:
            # In ghost mode, we fail silently. No logs, no console output.
            pass
        sys.exit()

    # If run normally, re-launch itself in the background and exit.
    else:
        print("Starting AshClip in the background...")
        
        command = [sys.executable, __file__, '--background']

        # Platform-specific logic to launch a detached, windowless process.
        if os.name == 'nt': # Windows
            subprocess.Popen(command, creationflags=subprocess.CREATE_NO_WINDOW)
        else: # macOS & Linux
            subprocess.Popen(command)
        
        print("AshClip is now running in ghost mode. You can close this terminal.")
        print("Hotkey: Ctrl+Shift+A (to fetch) | Ctrl+Z (to stop)")
        sys.exit()

if __name__ == "__main__":
    main()