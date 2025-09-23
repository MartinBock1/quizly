import yt_dlp
import whisper
import tempfile
import os


def extract_audio_from_youtube(url):
    """
    Downloads the audio from a YouTube URL as mp3 and returns the file path.
    Args:
        url (str): The YouTube video URL.
    Returns:
        str: Path to the downloaded mp3 file.
    """
    tmp_dir = tempfile.mkdtemp()
    tmp_filename = os.path.join(tmp_dir, '%(id)s.%(ext)s')
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": tmp_filename,
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_path = ydl.prepare_filename(info)
        audio_path = os.path.splitext(audio_path)[0] + '.mp3'
    return audio_path


def transcribe_audio(audio_path, model_name="base"):
    """
    Transcribes the audio file using Whisper and returns the transcript text.
    Args:
        audio_path (str): Path to the audio file.
        model_name (str): Whisper model name (default: "base").
    Returns:
        str: Transcribed text from the audio.
    """
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path)
    return result["text"]


def generate_quiz_with_gemini(transcript):
    """
    Sends the transcript to Gemini-Flash AI and receives quiz questions.
    Returns a list of questions with title, options, and answer.
    Args:
        transcript (str): The transcript text to generate questions from.
    Returns:
        list: List of question dicts with 'question_title', 'question_options', and 'answer'.
    """
    from quizzly_app.utils.gemini import gemini_generate_content
    prompt = (
        "Erstelle ein Quiz mit 10 Fragen und jeweils 4 Antwortmöglichkeiten aus folgendem Transkript. "
        "Gib die Fragen als JSON-Liste mit den Feldern 'question_title', 'question_options' und 'answer' zurück.\nTranskript:\n" + transcript
    )
    response = gemini_generate_content(prompt)
    import json
    # Entferne Markdown-Wrapper
    if response.strip().startswith('```json'):
        response = response.strip()[7:]
    if response.strip().endswith('```'):
        response = response.strip()[:-3]
    response = response.strip()
    try:
        questions = json.loads(response)
    except Exception:
        # Fallback: Dummy-Fragen falls Parsing fehlschlägt
        questions = []
        for i in range(10):
            questions.append({
                "question_title": f"[Dummy] KI/Parsing-Fehler – Beispiel-Frage {i+1}",
                "question_options": [
                    "Die KI konnte keine echte Antwort generieren.",
                    "Dies ist eine Dummy-Option.",
                    "Bitte prüfen Sie die Eingabedaten.",
                    "Kontaktieren Sie ggf. den Support."
                ],
                "answer": "Keine echte Antwort vorhanden (Dummy)"
            })
    return questions
