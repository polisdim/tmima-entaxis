# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess
import re
import threading
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

import server

RENDER_URL = "https://tmima-entaxis.onrender.com"

def get_desktop_dir():
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
        desktop_val, _ = winreg.QueryValueEx(key, "Desktop")
        winreg.CloseKey(key)
        return os.path.expandvars(desktop_val)
    except Exception:
        return os.path.join(os.path.expanduser('~'), 'Desktop')

def run_server_forever():
    """Keeps local Python server running forever with auto-recovery."""
    while True:
        try:
            server.run_server(8080)
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Server encountered error: {e}. Restarting in 2s...")
            time.sleep(2)

def run_render_keepalive_forever():
    """Sends periodic heartbeats to Render every 7 minutes to prevent free-tier sleep."""
    while True:
        try:
            req = urllib.request.Request(
                RENDER_URL,
                headers={"User-Agent": "TE-Inclusion-Watchdog/2.0"}
            )
            with urllib.request.urlopen(req, timeout=45) as res:
                if res.status == 200:
                    pass
        except Exception:
            pass
        # Sleep for 7 minutes (420 seconds) - Render sleeps after 15 min of inactivity
        time.sleep(420)

def run_tunnel_forever():
    """Keeps Cloudflare tunnel open with auto-reconnect and link export."""
    CLOUDFLARED_EXE = os.path.join(BASE_DIR, 'cloudflared.exe')
    if not os.path.exists(CLOUDFLARED_EXE):
        return

    while True:
        try:
            cmd = [CLOUDFLARED_EXE, 'tunnel', '--url', 'http://127.0.0.1:8080']
            process = subprocess.Popen(
                cmd,
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding='utf-8',
                errors='ignore',
                creationflags=0x08000000 if os.name == 'nt' else 0
            )

            url_saved = False
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                m = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                if m and not url_saved:
                    tunnel_url = m.group(0)
                    url_saved = True
                    link_content = f"""=====================================================
  ΕΞΥΠΝΟΣ ΒΟΗΘΟΣ ΤΜΗΜΑΤΟΣ ΕΝΤΑΞΗΣ - ΔΗΜ.Ω.Σ. ΞΑΝΘΗΣ
=====================================================
📱 Σύνδεσμος για το Tablet (από οποιοδήποτε Wi-Fi/4G):
{tunnel_url}

🔒 Κωδικός PIN Ασφαλείας: 1524

💻 Τοπική πρόσβαση από αυτόν τον Υπολογιστή:
http://localhost:8080
=====================================================
Ημερομηνία: {time.strftime('%d/%m/%Y %H:%M:%S')}
"""
                    with open(os.path.join(BASE_DIR, 'Tablet_Link.txt'), 'w', encoding='utf-8') as f:
                        f.write(link_content)
                    
                    try:
                        desktop_dir = get_desktop_dir()
                        if os.path.exists(desktop_dir):
                            with open(os.path.join(desktop_dir, 'Σύνδεσμος_Tablet.txt'), 'w', encoding='utf-8') as f:
                                f.write(link_content)
                    except Exception:
                        pass
            
            process.wait()
        except Exception:
            time.sleep(3)

def install_windows_startup():
    """Optionally creates a Windows Startup entry so service launches on boot."""
    try:
        startup_dir = os.path.join(os.environ.get('APPDATA', ''), r'Microsoft\Windows\Start Menu\Programs\Startup')
        if os.path.exists(startup_dir):
            vbs_source = os.path.join(BASE_DIR, 'Start_Assistant.vbs')
            if os.path.exists(vbs_source):
                dest_shortcut = os.path.join(startup_dir, 'Start_TE_Assistant.vbs')
                with open(vbs_source, 'r', encoding='utf-8') as src, open(dest_shortcut, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
    except Exception:
        pass

if __name__ == '__main__':
    install_windows_startup()

    # 1. Local Server Thread
    t_server = threading.Thread(target=run_server_forever, daemon=True)
    t_server.start()
    time.sleep(1.5)

    # 2. Render Anti-Sleep Keep-Alive Thread
    t_keepalive = threading.Thread(target=run_render_keepalive_forever, daemon=True)
    t_keepalive.start()

    # 3. Cloudflare Tunnel Loop (Main thread)
    run_tunnel_forever()
