import argparse
import re
import subprocess
from pathlib import Path

import requests


def run(cmd):
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)


def _get_title(query: str) -> str:
    """Return the title of the first YouTube search result for *query*."""
    try:
        res = subprocess.run(
            [
                "yt-dlp",
                "--get-title",
                f"ytsearch1:{query}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return ""
    return res.stdout.strip()


def _download(query: str, output: Path) -> None:
    """Download the first search result for *query* to *output*."""
    run(
        [
            "yt-dlp",
            "-f",
            "bestvideo[height>=1080]+bestaudio/best[height>=1080]",
            "-o",
            str(output),
            f"ytsearch1:{query}",
        ]
    )


def _strip_non_latin(text: str) -> str:
    """Remove CJK characters from *text* for broader search."""
    return re.sub(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]", "", text)


SUB_KEYWORDS = [
    "sub",
    "eng sub",
    "english sub",
    "sub español",
    "sub espanol",
    "sub spanish",
    "sub rus",
    "sub russian",
]


def search_sub_video(title: str, output: Path) -> str:
    """Search various variations of *title* for a subtitled video and download it."""
    bases = [title]
    sanitized = _strip_non_latin(title).strip()
    if sanitized and sanitized != title:
        bases.append(sanitized)

    queries: list[str] = []
    for base in bases:
        for keyword in SUB_KEYWORDS:
            queries.append(f"{base} {keyword}")
    queries.extend(bases)  # last resort: original title without keywords

    for query in queries:
        found = _get_title(query)
        if found:
            _download(query, output)
            return found
    raise RuntimeError("No subtitled video found")


def download_clean_video(title: str, output: Path) -> None:
    """Download the clean/original video for *title*."""
    found = _get_title(title)
    if not found:
        raise RuntimeError("No original video found")
    _download(title, output)


def get_resolution(video: Path) -> tuple[int, int]:
    """Return video width and height using ffprobe."""
    res = subprocess.run([
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "csv=s=x:p=0",
        str(video),
    ], capture_output=True, text=True, check=True)
    width, height = map(int, res.stdout.strip().split("x"))
    return width, height


def calc_subtitle_area(width: int, height: int) -> tuple[int, int, int, int]:
    """Estimate subtitle area based on resolution.

    Uses ratios derived from a 1080p sample where the region is
    ``843 1070 0 1920``.
    """
    y_min = int(height * 843 / 1080)
    y_max = int(height * 1070 / 1080)
    return y_min, y_max, 0, width


def extract_subtitles(video: Path, output: Path) -> None:
    """Extract subtitles from a video using the built-in extractor."""
    width, height = get_resolution(video)
    sub_area = calc_subtitle_area(width, height)
    from backend.main import SubtitleExtractor

    extractor = SubtitleExtractor(str(video), sub_area=sub_area)
    extractor.run()
    generated = video.with_suffix(".srt")
    generated.rename(output)


LANG_MAP = {
    "eng": "English",
    "english": "English",
    "sub español": "Spanish",
    "español": "Spanish",
    "espanol": "Spanish",
    "esp": "Spanish",
    "es": "Spanish",
    "рус": "Russian",
    "rus": "Russian",
    "ru": "Russian",
}


def detect_language(title: str) -> str:
    """Detect subtitle language from a video title."""
    match = re.search(r"\[(.+?)\]", title)
    if not match:
        return ""
    tag = match.group(1).lower()
    for key, lang in LANG_MAP.items():
        if key in tag:
            return lang
    return ""


def translate_subtitles(input_srt: Path, output_srt: Path, src_lang: str) -> None:
    """Translate subtitles using chatgpt-subtitle-translator."""
    cmd = [
        "chatgpt-subtitle-translator",
        "-i",
        str(input_srt),
        "-o",
        str(output_srt),
    ]
    if src_lang:
        cmd.extend(["--from", src_lang])
    run(cmd)


def burn_subtitles(video: Path, subtitles: Path, output: Path) -> None:
    """Burn subtitles into a video using ffmpeg."""
    run([
        "ffmpeg",
        "-i",
        str(video),
        "-vf",
        f"subtitles={subtitles}",
        str(output),
    ])


def send_telegram(video: Path, token: str, chat_id: str) -> None:
    """Send the resulting video to a Telegram user via bot API."""
    with video.open("rb") as f:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendVideo",
            data={"chat_id": chat_id},
            files={"video": f},
        )


def process(
    title: str,
    output: Path,
    workdir: Path,
    telegram_token: str | None = None,
    telegram_chat_id: str | None = None,
) -> None:
    """Run the full download/translate/burn pipeline for *title*."""
    workdir.mkdir(parents=True, exist_ok=True)
    sub_video = workdir / "sub_video.mp4"
    clean_video = workdir / "clean_video.mp4"
    raw_srt = workdir / "raw.srt"
    translated_srt = workdir / "translated.srt"

    sub_title = search_sub_video(title, sub_video)
    download_clean_video(title, clean_video)

    lang = detect_language(sub_title)
    extract_subtitles(sub_video, raw_srt)
    translate_subtitles(raw_srt, translated_srt, lang)
    burn_subtitles(clean_video, translated_srt, output)

    if telegram_token and telegram_chat_id:
        send_telegram(output, telegram_token, telegram_chat_id)


def main():
    parser = argparse.ArgumentParser(
        description="Search videos, translate subtitles and burn them"
    )
    parser.add_argument(
        "title", help="Title of the video to search for on YouTube"
    )
    parser.add_argument("output", help="Path to the output video with burned subtitles")
    parser.add_argument("--workdir", default="work", help="Working directory for intermediate files")
    parser.add_argument("--telegram-token", help="Telegram bot token")
    parser.add_argument("--telegram-chat-id", help="Telegram chat ID to send the video to")
    args = parser.parse_args()

    process(
        args.title,
        Path(args.output),
        Path(args.workdir),
        args.telegram_token,
        args.telegram_chat_id,
    )


if __name__ == "__main__":
    main()