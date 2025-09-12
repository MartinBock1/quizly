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
        
        url = request.data.get('url')
        if not url or not url.startswith('https://www.youtube.com/watch?v='):
            return Response({"detail": "Invalid YouTube URL."}, status=status.HTTP_400_BAD_REQUEST)

        # Videoinformationen mit yt-dlp extrahieren
        try:
            tmp_filename = '/tmp/%(id)s.%(ext)s'  # Beispiel für temporären Pfad
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": tmp_filename,
                "quiet": True,
                "noplaylist": True,
                "skip_download": True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Quiz Title')
            description = info.get('description', 'Quiz Description')
        except Exception:
            title = 'Quiz Title'
            description = 'Quiz Description'

        quiz = Quiz.objects.create(
            title=title,
            description=description,
            video_url=url,
            owner=request.user
        )
        question = Question.objects.create(
            quiz=quiz,
            question_title="Question 1",
            question_options=["Option A", "Option B", "Option C", "Option D"],
            answer="Option A"
        )

        from .serializers import QuizSerializer
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
