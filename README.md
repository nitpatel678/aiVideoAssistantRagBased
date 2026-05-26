# AI Video Assistant RAG Based

AI Video Assistant turns a YouTube URL or local media file into a transcript,
summary, action items, decisions, open questions, and a RAG-powered chat
interface.

## Live App

https://aivideoassistantragbased.streamlit.app/

## Run Locally

```powershell
cd C:\Users\HP\Desktop\aiVideoAssitantProject
.\venv\Scripts\activate
streamlit run app.py
```

Open `http://localhost:8501`.

## Environment Variables

Create a `.env` file locally or add these values as Streamlit secrets:

```env
MISTRAL_API_KEY=your_mistral_api_key
SARVAM_API_KEY=your_sarvam_api_key
SARVAM_STT_MODEL=saaras:v2.5
WHISPER_MODEL=tiny
EMBEDDING_DEVICE=cpu
```

`SARVAM_API_KEY` is required only for Hinglish mode.

## Deploy On Streamlit Community Cloud

1. Push this repository to GitHub.
2. Go to `https://share.streamlit.io`.
3. Sign in with GitHub.
4. Click `New app`.
5. Select this repository: `nitpatel678/aiVideoAssistantRagBased`.
6. Select branch: `main`.
7. Set main file path: `app.py`.
8. Open `Advanced settings`.
9. Add secrets:

```toml
MISTRAL_API_KEY = "your_mistral_api_key"
SARVAM_API_KEY = "your_sarvam_api_key"
SARVAM_STT_MODEL = "saaras:v2.5"
WHISPER_MODEL = "tiny"
EMBEDDING_DEVICE = "cpu"
```

10. Click `Deploy`.

The repo includes `requirements.txt` for Python packages and `packages.txt` for
the FFmpeg system package required by audio processing. `runtime.txt` pins
Python 3.11 for better compatibility with Chroma, protobuf, Whisper, and
PyTorch on Streamlit Cloud.
