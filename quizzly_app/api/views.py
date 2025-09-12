from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import yt_dlp

from quizzly_app.models import Quiz, Question


# Custom JWT Authentication that reads token from cookie
class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')
        if access_token:
            try:
                validated_token = self.get_validated_token(access_token)
                return self.get_user(validated_token), validated_token
            except Exception:
                return None
        return super().authenticate(request)


class CreateQuizView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        from quizzly_app.utils.quiz_pipeline import extract_audio_from_youtube, transcribe_audio, generate_quiz_with_gemini
        url = request.data.get('url')
        if not url or not url.startswith('https://www.youtube.com/watch?v='):
            return Response({"detail": "Invalid YouTube URL."}, status=status.HTTP_400_BAD_REQUEST)

        # Schritt 1: Audio extrahieren
        try:
            audio_path = extract_audio_from_youtube(url)
        except Exception as e:
            return Response({"detail": f"Audio extraction failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Schritt 2: Transkribieren
        try:
            transcript = transcribe_audio(audio_path, model_name="base")
        except Exception as e:
            return Response({"detail": f"Transcription failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Schritt 3: Quizfragen generieren
        try:
            questions_data = generate_quiz_with_gemini(transcript)
        except Exception as e:
            return Response({"detail": f"Quiz generation failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Schritt 4: Quiz speichern
        quiz = Quiz.objects.create(
            title=f"Quiz zu {url}",
            description="Automatisch generiert aus YouTube-Video.",
            video_url=url,
            owner=request.user
        )
        for q in questions_data:
            Question.objects.create(
                quiz=quiz,
                question_title=q["question_title"],
                question_options=q["question_options"],
                answer=q["answer"]
            )

        from .serializers import QuizSerializer
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
