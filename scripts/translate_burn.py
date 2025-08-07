import argparse
import subprocess
from pathlib import Path


def run(cmd):
    print(' '.join(cmd))
    subprocess.run(cmd, check=True)


def download_video(url: str, output: Path) -> None:
    """Download video from a URL using yt-dlp.

    The function downloads the best available stream at 1080p or higher.
    """
    run([
        "yt-dlp",
        "-f",
        "bestvideo[height>=1080]+bestaudio/best[height>=1080]",
        "-o",
        str(output),
        url,
    ])


def extract_subtitles(video: Path, output: Path) -> None:
    """Extract the first subtitle track from a video with ffmpeg."""
    run([
        "ffmpeg",
        "-i",
        str(video),
        "-map",
        "0:s:0",
        str(output),
    ])


def translate_subtitles(input_srt: Path, output_srt: Path) -> None:
    """Translate subtitles using chatgpt-subtitle-translator."""
    run([
        "chatgpt-subtitle-translator",
        str(input_srt),
        str(output_srt),
    ])


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


def main():
    parser = argparse.ArgumentParser(description="Download videos, translate subtitles and burn them")
    parser.add_argument("subtitle_video", help="URL of video that contains subtitles")
    parser.add_argument("clean_video", help="URL of video without subtitles")
    parser.add_argument("output", help="Path to the output video with burned subtitles")
    parser.add_argument("--workdir", default="work", help="Working directory for intermediate files")
    args = parser.parse_args()

    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    sub_video = workdir / "sub_video.mp4"
    clean_video = workdir / "clean_video.mp4"
    raw_srt = workdir / "raw.srt"
    translated_srt = workdir / "translated.srt"

    download_video(args.subtitle_video, sub_video)
    download_video(args.clean_video, clean_video)

    extract_subtitles(sub_video, raw_srt)
    translate_subtitles(raw_srt, translated_srt)
    burn_subtitles(clean_video, translated_srt, Path(args.output))


if __name__ == "__main__":
    main()
