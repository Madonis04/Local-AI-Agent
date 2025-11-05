# agent/tools/app_launcher.py

import os
import subprocess
import platform
import webbrowser
import re

def open_application(app_path):
    """Opens an application given its full path or executable name."""
    os_type = platform.system()
    try:
        if os_type == "Windows":
            os.startfile(app_path)
        elif os_type == "Darwin":  # macOS
            subprocess.Popen(["open", app_path])
        elif os_type == "Linux":
            subprocess.Popen([app_path])
        else:
            print(f"Unsupported OS: {os_type}")
    except Exception as e:
        print(f"[ERROR] Unable to open application '{app_path}': {e}")

def open_vscode():
    """Opens Visual Studio Code using the 'code' command line tool."""
    try:
        subprocess.Popen("code", shell=True)
    except FileNotFoundError:
        print("[ERROR] 'code' command not found. Ensure VS Code is in your system's PATH.")
    except Exception as e:
        print(f"[ERROR] Unable to open VS Code: {e}")

def open_url(url):
    """
    Opens a URL in the default browser. Adds 'https://' if missing.
    """
    try:
        # If the user just says "youtube.com", we need to add the protocol
        if not re.match(r"^(https?://)", url):
            url = "https://" + url
        webbrowser.open(url)
        return f"Opening {url} in the browser."
    except Exception as e:
        return f"[ERROR] Unable to open URL: {e}"

def open_Youtube(query):
    """Opens the default browser to a Youtube for the given query."""
    try:
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return f"Searching YouTube for '{query}'."
    except Exception as e:
        return f"[ERROR] Unable to perform Youtube: {e}"