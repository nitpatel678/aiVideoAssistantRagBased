import yt_dlp
from pydub import AudioSegment
import os

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

def convert_to_wav(input_file:str) -> str:
    output_path = os.path.splitext(input_file)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_file)
    audio = audio.set_frame_rate(16000).set_channels(1) #16kHz, mono
    audio.export(output_path, format='wav')
    return output_path


def chunk_audio(wav_path : str , chunk_minutes : int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_length_ms = chunk_minutes * 60 * 1000
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]
        chunk_path = f"{os.path.splitext(wav_path)[0]}_chunk_{i//chunk_length_ms}.wav"
        chunk.export(chunk_path, format='wav')
        chunks.append(chunk_path)
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