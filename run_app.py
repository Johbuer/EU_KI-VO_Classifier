import os
import sys

if False:
    import app
    import fpdf

base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
os.chdir(base_path)

os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
os.environ["STREAMLIT_SERVER_PORT"] = "8501"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"

import webbrowser
import threading
import time
import streamlit.web.bootstrap as bootstrap


def open_browser():
    time.sleep(2.5)
    url = "http://localhost:8501"
    
    import subprocess
    
    if sys.platform == "darwin":
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        ]
        for path in paths:
            if os.path.exists(path):
                try:
                    subprocess.Popen([path, f"--app={url}"])
                    return
                except Exception:
                    pass
                    
    elif sys.platform == "win32":
        paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
        ]
        for path in paths:
            if os.path.exists(path):
                try:
                    subprocess.Popen([path, f"--app={url}"])
                    return
                except Exception:
                    pass

    webbrowser.open(url)


if __name__ == "__main__":
    app_path = os.path.join(base_path, "app.py")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    sys.argv = [
        "streamlit", "run", app_path,
        "--global.developmentMode=false",
        "--server.headless=true",
        "--server.port=8501"
    ]
    
    flag_options = {
        "global.developmentMode": False,
        "server.port": 8501,
        "server.headless": True
    }
    bootstrap.run(app_path, False, [], flag_options=flag_options)
