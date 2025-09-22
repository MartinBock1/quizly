from ..models import Quiz
from .serializers import QuizSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from user_auth_app.api.views import CookieJWTAuthentication

from .helpers import (
    update_quiz_partial,
    create_quiz_from_youtube,
    create_dummy_quiz,
    serialize_user_quizzes,
    serialize_quiz_detail,
    delete_quiz
)


class CreateQuizView(APIView):
    """
    API endpoint for creating a quiz from a YouTube video URL.
    Requires authentication. Uses Gemini AI for quiz generation.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        """
        Handles POST requests to create a quiz from a YouTube URL.
        Returns the created quiz data or a dummy quiz on error.
        """
        url = request.data.get('url')
        if not url or not url.startswith('https://www.youtube.com/watch?v='):
            return Response({"detail": "Invalid YouTube URL."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            quiz_data = create_quiz_from_youtube(url, request.user)
            return Response(quiz_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            error_msg = f"Quiz creation failed: {str(e)}"
            return self._dummy_quiz_response(url, request.user, error_msg)

    def _dummy_quiz_response(self, url, user, error_msg):
        """
        Helper method to return a dummy quiz response if quiz creation fails.
        """
        data = create_dummy_quiz(url, user, error_msg)
        return Response(data, status=status.HTTP_201_CREATED)


class UserQuizListView(APIView):
    """
    API endpoint for listing all quizzes belonging to the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        """
        Handles GET requests to retrieve all quizzes for the current user.
        """
        data = serialize_user_quizzes(request.user)
        return Response(data, status=status.HTTP_200_OK)


class UserQuizDetailView(APIView):
    """
    API endpoint for retrieving, updating, or deleting a specific quiz by ID.
    Only allows access to quizzes owned by the authenticated user.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request, id):
        """
        Handles GET requests to retrieve details of a specific quiz.
        Returns 404 if not found, 403 if not owned by user.
        """
        try:
            quiz = Quiz.objects.get(pk=id)
        except Quiz.DoesNotExist:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        if quiz.owner != request.user:
            return Response({"detail": "Access denied. Quiz does not belong to user."}, status=status.HTTP_403_FORBIDDEN)
        data = serialize_quiz_detail(quiz)
        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        """
        Handles PATCH requests to partially update a quiz's fields.
        Only allows updates by the quiz owner.
        """
        try:
            quiz = Quiz.objects.get(pk=id)
        except Quiz.DoesNotExist:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        if quiz.owner != request.user:
            return Response({"detail": "Access denied. Quiz does not belong to user."}, status=status.HTTP_403_FORBIDDEN)
        quiz = update_quiz_partial(quiz, request.data)
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        """
        Handles DELETE requests to remove a quiz from the database.
        Only allows deletion by the quiz owner.
        """
        try:
            quiz = Quiz.objects.get(pk=id)
        except Quiz.DoesNotExist:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        if quiz.owner != request.user:
            return Response({"detail": "Access denied. Quiz does not belong to user."}, status=status.HTTP_403_FORBIDDEN)
        data = delete_quiz(quiz)
        return Response(data, status=status.HTTP_204_NO_CONTENT)
