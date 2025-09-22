from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status


class CreateQuizTests(APITestCase):
    """
    Test suite for the quiz creation API endpoint.
    Covers error handling, authentication, and response structure.
    """

    def test_create_quiz_whisper_error(self):
        """
        Test: Quiz creation fails due to Whisper transcription error.
        Expects a dummy quiz and error detail in the response.
        """
        from unittest.mock import patch
        with patch('quizzly_app.utils.quiz_pipeline.extract_audio_from_youtube', return_value='dummy_path.wav'):
            with patch('quizzly_app.utils.quiz_pipeline.transcribe_audio', side_effect=Exception('Whisper failed!')):
                data = {"url": "https://www.youtube.com/watch?v=3ohjOltaO6Y"}
                response = self.client.post(self.url, data, format='json')
                self.assertEqual(response.status_code, 201)
                self.assertIn('Transcription failed', response.data['detail'])
                self.assertIn('dummy_quiz', response.data)
                quiz = response.data['dummy_quiz']
                self.assertIn('questions', quiz)

    def test_create_quiz_ytdlp_error(self):
        """
        Test: Quiz creation fails due to yt-dlp error (invalid YouTube ID).
        Expects a dummy quiz in the response.
        """
        data = {"url": "https://www.youtube.com/watch?v=invalidid"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('dummy_quiz', response.data)
        quiz = response.data['dummy_quiz']
        self.assertIn('title', quiz)
        self.assertIn('description', quiz)

    def test_create_quiz_no_questions(self):
        """
        Test: Quiz creation results in no questions.
        Expects an empty questions list in the serialized quiz.
        """
        data = {"url": "https://www.youtube.com/watch?v=example"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('dummy_quiz', response.data)
        quiz = response.data['dummy_quiz']
        self.assertIn('questions', quiz)
        # Frage entfernen und Quiz erneut serialisieren
        from quizzly_app.models import Quiz
        quiz_obj = Quiz.objects.last()
        quiz_obj.questions.all().delete()
        from quizzly_app.api.serializers import QuizSerializer
        serializer = QuizSerializer(quiz_obj)
        self.assertEqual(serializer.data['questions'], [])

    def setUp(self):
        """
        Set up a test user and authenticate the test client.
        """
        self.user = get_user_model().objects.create_user(
            username='quizuser',
            email='quizuser@example.com',
            password='quizpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('create_quiz')

    def test_create_quiz_success(self):
        """
        Test: Successful quiz creation with a valid YouTube URL.
        Checks for all required quiz and question fields in the response.
        Handles both dummy and real quiz cases.
        """
        data = {"url": "https://www.youtube.com/watch?v=example"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Bei Dummy-Quiz liegen die Daten unter 'dummy_quiz', sonst direkt
        if 'dummy_quiz' in response.data:
            quiz = response.data['dummy_quiz']
        else:
            quiz = response.data
        self.assertIn('id', quiz)
        self.assertIn('title', quiz)
        self.assertIn('description', quiz)
        self.assertIn('video_url', quiz)
        self.assertIn('questions', quiz)
        self.assertIsInstance(quiz['questions'], list)
        if quiz['questions']:
            question = quiz['questions'][0]
            self.assertIn('id', question)
            self.assertIn('question_title', question)
            self.assertIn('question_options', question)
            self.assertIn('answer', question)

    def test_create_quiz_invalid_url(self):
        """
        Test: Quiz creation with an invalid YouTube URL.
        Expects a 400 Bad Request and error detail in the response.
        """
        data = {"url": "not_a_youtube_url"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_create_quiz_unauthenticated(self):
        """
        Test: Quiz creation without authentication.
        Expects a 401 Unauthorized and error detail in the response.
        """
        self.client.force_authenticate(user=None)
        data = {"url": "https://www.youtube.com/watch?v=example"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
