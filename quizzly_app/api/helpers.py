from ..models import Quiz, Question
from .serializers import QuizSerializer

def update_quiz_partial(quiz, data):
    """
    Partially updates a Quiz instance with provided data.
    Only updates fields present in the data dict (title, description, video_url).
    Returns the updated Quiz instance.
    """
    updated = False
    if "title" in data:
        quiz.title = data["title"]
        updated = True
    if "description" in data:
        quiz.description = data["description"]
        updated = True
    if "video_url" in data:
        quiz.video_url = data["video_url"]
        updated = True
    if updated:
        quiz.save()
    return quiz

def create_quiz_from_youtube(url, user):
    """
    Creates a Quiz from a YouTube URL for the given user.
    Extracts audio, transcribes it, generates questions using Gemini AI,
    and saves the quiz and its questions to the database.
    Returns serialized quiz data.
    """
    from quizzly_app.utils.quiz_pipeline import extract_audio_from_youtube, transcribe_audio, generate_quiz_with_gemini
    audio_path = extract_audio_from_youtube(url)
    transcript = transcribe_audio(audio_path, model_name="base")
    questions_data = generate_quiz_with_gemini(transcript)
    quiz = Quiz.objects.create(
        title=f"Quiz zu {url}",
        description="Automatisch generiert aus YouTube-Video.",
        video_url=url,
        owner=user
    )
    for q in questions_data:
        Question.objects.create(
            quiz=quiz,
            question_title=q["question_title"],
            question_options=q["question_options"],
            answer=q["answer"]
        )
    serializer = QuizSerializer(quiz)
    return serializer.data

def create_dummy_quiz(url, user, error_msg):
    """
    Creates a dummy Quiz for the given user and YouTube URL.
    Used as a fallback if quiz generation fails.
    Returns a dict with error details and serialized dummy quiz data.
    """
    from quizzly_app.utils.quiz_pipeline import generate_quiz_with_gemini
    questions_data = generate_quiz_with_gemini("DUMMY")
    quiz = Quiz.objects.create(
        title=f"Beispiel-Quiz zu {url}",
        description=error_msg,
        video_url=url,
        owner=user
    )
    for q in questions_data:
        Question.objects.create(
            quiz=quiz,
            question_title=q["question_title"],
            question_options=q["question_options"],
            answer=q["answer"]
        )
    serializer = QuizSerializer(quiz)
    return {
        "detail": error_msg,
        "dummy_quiz": serializer.data
    }

def serialize_user_quizzes(user):
    """
    Serializes all quizzes belonging to the given user, ordered by creation date (descending).
    Returns a list of serialized quiz data.
    """
    quizzes = Quiz.objects.filter(owner=user).order_by('-created_at')
    serializer = QuizSerializer(quizzes, many=True)
    return serializer.data

def serialize_quiz_detail(quiz):
    """
    Serializes a single Quiz instance.
    Returns serialized quiz data.
    """
    serializer = QuizSerializer(quiz)
    return serializer.data

def delete_quiz(quiz):
    """
    Deletes the given Quiz instance from the database.
    Returns a dict with a success message.
    """
    quiz.delete()
    return {"detail": "Quiz deleted successfully."}
