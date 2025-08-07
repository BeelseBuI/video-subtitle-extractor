import json
import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = REPO_ROOT / "host_config.json"
REQUIREMENTS_FILE = REPO_ROOT / "requirements.txt"


def ensure_requirements():
    """Install required packages if missing."""
    try:
        import flask  # noqa: F401
    except ImportError:
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            str(REQUIREMENTS_FILE),
        ])


def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {
        "output": "output.mp4",
        "workdir": "work",
        "host": "127.0.0.1",
        "port": "5000",
        "telegram_token": "",
        "telegram_chat_id": "",
    }


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2)


def run_server(cfg):
    from web_server import create_app

    app_cfg = {
        "output": Path(cfg["output"]),
        "workdir": Path(cfg["workdir"]),
        "telegram_token": cfg.get("telegram_token") or None,
        "telegram_chat_id": cfg.get("telegram_chat_id") or None,
    }
    app = create_app(app_cfg)
    thread = threading.Thread(
        target=app.run,
        kwargs={"host": cfg["host"], "port": int(cfg["port"])},
        daemon=True,
    )
    thread.start()
    messagebox.showinfo(
        "Server Running",
        f"Open http://{cfg['host']}:{cfg['port']} in your browser.",
    )


def main():
    ensure_requirements()
    cfg = load_config()

    root = tk.Tk()
    root.title("Subtitle Web Server")

    entries = {}
    labels = [
        ("output", "Output video path"),
        ("workdir", "Working directory"),
        ("host", "Host"),
        ("port", "Port"),
        ("telegram_token", "Telegram token"),
        ("telegram_chat_id", "Telegram chat ID"),
    ]

    for i, (key, label) in enumerate(labels):
        tk.Label(root, text=label).grid(row=i, column=0, sticky="e")
        entry = tk.Entry(root, width=40)
        entry.grid(row=i, column=1)
        entry.insert(0, cfg.get(key, ""))
        entries[key] = entry

    def save():
        new_cfg = {k: entries[k].get().strip() for k in entries}
        save_config(new_cfg)
        messagebox.showinfo("Saved", "Settings saved")

    def start():
        new_cfg = {k: entries[k].get().strip() for k in entries}
        save_config(new_cfg)
        run_server(new_cfg)

    tk.Button(root, text="Save Settings", command=save).grid(row=len(labels), column=0)
    tk.Button(root, text="Start Server", command=start).grid(row=len(labels), column=1)

    root.mainloop()


if __name__ == "__main__":
    main()
