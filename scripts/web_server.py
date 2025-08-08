import argparse
from pathlib import Path

from flask import Flask, render_template_string, request

import sys
# добавляем в пути корень проекта (папку над scripts/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from translate_burn import process

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Subtitle Translator</title>
  <style>
    body {
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'Segoe UI', Roboto, Oxygen,
        Ubuntu, Cantarell, 'Open Sans', sans-serif;
      background-color: #f5f5f7;
      color: #1d1d1f;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
    }
    .card {
      background: #fff;
      padding: 40px;
      border-radius: 20px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.1);
      text-align: center;
      width: 100%;
      max-width: 480px;
    }
    h1 {
      font-weight: 600;
      margin-bottom: 20px;
    }
    input[type="text"] {
      width: 100%;
      padding: 12px 20px;
      margin: 8px 0;
      box-sizing: border-box;
      border: 1px solid #d2d2d7;
      border-radius: 12px;
      font-size: 16px;
    }
    input[type="submit"] {
      background-color: #0071e3;
      color: white;
      padding: 12px 24px;
      border: none;
      border-radius: 12px;
      font-size: 16px;
      cursor: pointer;
      margin-top: 10px;
    }
    input[type="submit"]:hover {
      background-color: #005bb5;
    }
    p.message {
      margin-top: 20px;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>Subtitle Translator</h1>
    <form method="post">
      <input type="text" name="title" placeholder="Enter video title" required>
      <input type="submit" value="Run">
    </form>
    {% if message %}<p class="message">{{ message }}</p>{% endif %}
  </div>
</body>
</html>
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
    parser.add_argument("--host", default="0.0.0.0", help="Host for the web server")
    parser.add_argument("--port", type=int, default=30000, help="Port for the web server")
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
