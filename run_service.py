# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess
import re
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

import server

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
    server.run_server(8080)

def run_tunnel_forever():
    CLOUDFLARED_EXE = os.path.join(BASE_DIR, 'cloudflared.exe')
    if not os.path.exists(CLOUDFLARED_EXE):
        return

    while True:
        try:
            cmd = [CLOUDFLARED_EXE, 'tunnel', '--url', 'http://localhost:8080']
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
            for line in iter(process.stdout.readline, ''):
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
            time.sleep(2)

if __name__ == '__main__':
    t = threading.Thread(target=run_server_forever, daemon=True)
    t.start()
    time.sleep(1.5)
    run_tunnel_forever()
