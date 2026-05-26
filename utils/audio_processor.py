import yt_dlp
import glob
import os
import subprocess
import tempfile

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def get_cookie_file() -> str | None:
    cookie_path = os.getenv("YOUTUBE_COOKIES_PATH")
    if cookie_path:
        return cookie_path

    cookie_text = os.getenv("YOUTUBE_COOKIES_TEXT")
    if not cookie_text:
        return None

    cookie_file = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False,
        encoding="utf-8",
    )
    cookie_file.write(cookie_text)
    cookie_file.close()
    return cookie_file.name

def download_youtube_audio(url:str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "outtmpl": output_path,
        "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "retries": 5,
        "fragment_retries": 5,
        "force_ipv4": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["default,-android_sdkless"],
            }
        },
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }],
    }
    cookie_file = get_cookie_file()
    if cookie_file:
        ydl_opts["cookiefile"] = cookie_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            # actual output after conversion
            filename = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"
    except yt_dlp.utils.DownloadError as exc:
        message = str(exc)
        if "403" in message or "Forbidden" in message:
            raise RuntimeError(
                "YouTube blocked the download request from this cloud server "
                "(HTTP 403). Try again, use a different video, or add YouTube "
                "cookies in Streamlit secrets as YOUTUBE_COOKIES_TEXT."
            ) from exc
        raise RuntimeError(f"Could not download YouTube audio: {message}") from exc

    return filename

def run_ffmpeg(args: list[str]) -> None:
    command = ["ffmpeg", "-y", *args]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def convert_to_wav(input_file:str) -> str:
    output_path = os.path.splitext(input_file)[0] + "_converted.wav"
    run_ffmpeg(["-i", input_file, "-ar", "16000", "-ac", "1", output_path])
    return output_path


def chunk_audio(wav_path : str , chunk_minutes : int = 10) -> list:
    chunk_seconds = chunk_minutes * 60
    chunk_pattern = f"{os.path.splitext(wav_path)[0]}_chunk_%03d.wav"
    run_ffmpeg([
        "-i",
        wav_path,
        "-f",
        "segment",
        "-segment_time",
        str(chunk_seconds),
        "-c",
        "copy",
        chunk_pattern,
    ])
    chunks = sorted(glob.glob(chunk_pattern.replace("%03d", "*")))
    if not chunks:
        chunks = [wav_path]
    return chunks

def process_input(source:str) -> list:
    if source.startswith("http")or source.startswith("www") or source.startswith("https"):
        print(f"Downloading audio from YouTube: {source}")
        audio_path = download_youtube_audio(source)
    else:
        print(f"Processing local audio file: {source}")
        audio_path = source

    print(f"Converting audio to WAV format: {audio_path}")
    wav_path = convert_to_wav(audio_path)
    chunks = chunk_audio(wav_path)
    print(f"Audio processing complete. Generated {len(chunks)} chunks.")
    return chunks
