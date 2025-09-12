from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import RegistrationSerializer

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that reads the access token from cookies.

    This class overrides the default JWTAuthentication to retrieve the access token
    from the 'access_token' cookie. If the token is present and valid, it authenticates
    the user. Otherwise, it falls back to the default authentication method.

    Args:
        request (Request): The HTTP request object.

    Returns:
        tuple: (user, validated_token) if authentication is successful.
        None: if authentication fails.
    """

    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')
        if access_token:
            try:
                validated_token = self.get_validated_token(access_token)
                return self.get_user(validated_token), validated_token
            except Exception:
                return None
        return super().authenticate(request)


class RegistrationView(APIView):
    """
    API endpoint for user registration.

    Allows any user (authenticated or not) to register by sending a POST request
    with user data. If the data is valid, a new user account is created.

    Permissions:
        AllowAny: No authentication required.

    Methods:
        post(request): Handles user registration.

    Returns:
        Response: 201 Created with success message if registration succeeds.
                  400 Bad Request with validation errors if registration fails.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles user registration.

        Args:
            request (Request): The HTTP request containing user registration data.

        Returns:
            Response: Success message or validation errors.
        """
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            data = {
                "detail": "User created successfully!"
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CookieTokenObtainPairView(TokenObtainPairView):
    """
    API endpoint for user login using JWT tokens stored in cookies.

    Extends TokenObtainPairView to:
    - Validate user credentials and issue JWT tokens.
    - Set access and refresh tokens as secure, HTTPOnly cookies.
    - Return user information and a success message in the response.

    Security:
        - Cookies are HTTPOnly and secure to prevent XSS.
        - Tokens are not exposed in the response body.

    Methods:
        post(request): Handles user login and sets JWT cookies.

    Returns:
        Response: 200 OK with user info and cookies if login succeeds.
                  401 Unauthorized if credentials are invalid.
    """

    def post(self, request, *args, **kwargs):
        """
        Handles user login and sets JWT tokens as secure cookies.

        Args:
            request (Request): The HTTP request containing user credentials.

        Returns:
            Response: Success message, user info, and cookies if login succeeds.
                      401 Unauthorized if credentials are invalid.
        """
        serializer = self.get_serializer(data=request.data)
        from rest_framework.exceptions import ValidationError
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response({"detail": "Invalid credentials!"}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.user
        access = serializer.validated_data.get("access")
        refresh = serializer.validated_data.get("refresh")
        response = Response()

        response.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=False,  # Für lokale Entwicklung
            samesite="Lax",
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=False,  # Für lokale Entwicklung
            samesite="Lax",
        )
        response.status_code = status.HTTP_200_OK
        response.data = {
            "detail": "Login successfully!",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }
        return response


class CookieTokenRefreshView(TokenRefreshView):
    """
    API endpoint to refresh JWT access token using a refresh token from cookies.

    Extends TokenRefreshView to read the refresh token from the 'refresh_token' cookie.
    If valid, issues a new access token and sets it as a secure, HTTPOnly cookie.

    Methods:
        post(request): Handles access token refresh.

    Returns:
        Response: 200 OK with new access token cookie if refresh succeeds.
                  400 Bad Request if refresh token is missing.
                  401 Unauthorized if refresh token is invalid.
    """

    def post(self, request, *args, **kwargs):
        """
        Handles access token refresh using refresh token from cookies.

        Args:
            request (Request): The HTTP request.

        Returns:
            Response: Success message and new access token cookie if refresh succeeds.
                      Error message if refresh token is missing or invalid.
        """
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response(
                {"detail": "Refresh token invalid!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        access_token = serializer.validated_data.get("access")
        response = Response({
            "detail": "Token refreshed",
            "access": access_token
        })
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Für lokale Entwicklung
            samesite="Lax",
        )
        return response


class LogoutView(APIView):
    """
    API endpoint for user logout.

    Deletes access and refresh tokens from cookies and blacklists the refresh token.
    Only authenticated users can access this endpoint.

    Permissions:
        IsAuthenticated: User must be authenticated.
    Authentication:
        CookieJWTAuthentication: Uses JWT tokens from cookies.

    Methods:
        post(request): Handles user logout.

    Returns:
        Response: 200 OK with logout success message.
                  500 Internal Server Error if logout fails.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        """
        Handles user logout by deleting tokens and cookies.

        Args:
            request (Request): The HTTP request.

        Returns:
            Response: Success message if logout succeeds.
                      Error message if logout fails.
        """
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception:
                    pass  # Ignore if token is already invalid

            response = Response({
                "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
            }, status=status.HTTP_200_OK)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response
        except Exception:
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
