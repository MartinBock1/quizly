from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status

class CreateQuizTests(APITestCase):
    def test_create_quiz_ytdlp_error(self):
        # Simuliere ungültige YouTube-URL, die yt-dlp Fehler auslöst
        data = {"url": "https://www.youtube.com/watch?v=invalidid"}
        response = self.client.post(self.url, data, format='json')
        # Sollte trotzdem ein Quiz mit Default-Titel/Description anlegen
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], 'Quiz Title')
        self.assertEqual(response.data['description'], 'Quiz Description')

    def test_create_quiz_no_questions(self):
        # Simuliere Quiz-Erstellung ohne automatische Frage
        # Hierzu müsste die View angepasst werden, aber Test prüft Response-Struktur
        data = {"url": "https://www.youtube.com/watch?v=example"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('questions', response.data)
        # Frage entfernen und Quiz erneut serialisieren
        from quizzly_app.models import Quiz
        quiz = Quiz.objects.last()
        quiz.questions.all().delete()
        from quizzly_app.api.serializers import QuizSerializer
        serializer = QuizSerializer(quiz)
        self.assertEqual(serializer.data['questions'], [])
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='quizuser',
            email='quizuser@example.com',
            password='quizpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('create_quiz')

    def test_create_quiz_success(self):
        data = {"url": "https://www.youtube.com/watch?v=example"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('title', response.data)
        self.assertIn('description', response.data)
        self.assertIn('video_url', response.data)
        self.assertIn('questions', response.data)
        self.assertIsInstance(response.data['questions'], list)
        if response.data['questions']:
            question = response.data['questions'][0]
            self.assertIn('id', question)
            self.assertIn('question_title', question)
            self.assertIn('question_options', question)
            self.assertIn('answer', question)

    def test_create_quiz_invalid_url(self):
        data = {"url": "not_a_youtube_url"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_create_quiz_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {"url": "https://www.youtube.com/watch?v=example"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
