import yt_dlp
import glob
import os
import subprocess

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_youtube_audio(url:str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        'outtmpl': output_path,
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

        # actual output after conversion
        filename = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"

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
