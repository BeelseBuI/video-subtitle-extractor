import argparse
from pathlib import Path

from flask import Flask, render_template_string, request

from translate_burn import process

HTML = """
<!doctype html>
<title>Subtitle Translator</title>
<h1>Enter video title</h1>
<form method="post">
  <input type="text" name="title" required>
  <input type="submit" value="Run">
</form>
{% if message %}<p>{{ message }}</p>{% endif %}
"""


def create_app(cfg):
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            title = request.form["title"].strip()
            try:
                process(
                    title,
                    cfg["output"],
                    cfg["workdir"],
                    cfg.get("telegram_token"),
                    cfg.get("telegram_chat_id"),
                )
                msg = "Processing completed"
            except Exception as exc:  # pragma: no cover - user-facing error
                msg = f"Error: {exc}"
            return render_template_string(HTML, message=msg)
        return render_template_string(HTML, message=None)

    return app


def main():
    parser = argparse.ArgumentParser(description="Run web UI for the subtitle pipeline")
    parser.add_argument("--output", default="output.mp4", help="Output video path")
    parser.add_argument("--workdir", default="work", help="Working directory")
    parser.add_argument("--telegram-token", help="Telegram bot token")
    parser.add_argument("--telegram-chat-id", help="Telegram chat ID")
    parser.add_argument("--host", default="127.0.0.1", help="Host for the web server")
    parser.add_argument("--port", type=int, default=5000, help="Port for the web server")
    args = parser.parse_args()

    cfg = {
        "output": Path(args.output),
        "workdir": Path(args.workdir),
        "telegram_token": args.telegram_token,
        "telegram_chat_id": args.telegram_chat_id,
    }

    app = create_app(cfg)
    app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()