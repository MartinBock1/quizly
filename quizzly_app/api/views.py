from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from user_auth_app.api.views import CookieJWTAuthentication

from ..models import Quiz, Question
from .serializers import QuizSerializer


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
            error_msg = f"Audio extraction failed: {str(e)}"
            return self._dummy_quiz_response(url, request.user, error_msg)

        try:
            transcript = transcribe_audio(audio_path, model_name="base")
        except Exception as e:
            error_msg = f"Transcription failed: {str(e)}"
            return self._dummy_quiz_response(url, request.user, error_msg)

        try:
            questions_data = generate_quiz_with_gemini(transcript)
        except Exception as e:
            error_msg = f"Quiz generation failed: {str(e)}"
            return self._dummy_quiz_response(url, request.user, error_msg)

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

    def _dummy_quiz_response(self, url, user, error_msg):
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
        from .serializers import QuizSerializer
        serializer = QuizSerializer(quiz)
        return Response({
            "detail": error_msg,
            "dummy_quiz": serializer.data
        }, status=status.HTTP_201_CREATED)


class UserQuizListView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        quizzes = Quiz.objects.filter(owner=request.user).order_by('-created_at')
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserQuizDetailView(APIView):
    

    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request, id):
        try:
            quiz = Quiz.objects.get(pk=id)
        except Quiz.DoesNotExist:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        if quiz.owner != request.user:
            return Response({"detail": "Access denied. Quiz does not belong to user."}, status=status.HTTP_403_FORBIDDEN)
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        try:
            quiz = Quiz.objects.get(pk=id)
        except Quiz.DoesNotExist:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        if quiz.owner != request.user:
            return Response({"detail": "Access denied. Quiz does not belong to user."}, status=status.HTTP_403_FORBIDDEN)
        serializer = QuizSerializer(quiz, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        try:
            quiz = Quiz.objects.get(pk=id)
        except Quiz.DoesNotExist:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        if quiz.owner != request.user:
            return Response({"detail": "Access denied. Quiz does not belong to user."}, status=status.HTTP_403_FORBIDDEN)
        quiz.delete()
        return Response({"detail": "Quiz deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
