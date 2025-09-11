from rest_framework import status
from .serializers import RegistrationSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

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


class RegistrationView(APIView):
    """
    Handles the creation of new users.

    This view allows any user (authenticated or not) to submit their registration
    details via a POST request. If the data is valid, a new user account is
    created, and their basic information is returned.
    """
    # Set permission to AllowAny, so that unauthenticated users can access this endpoint.
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Processes the user registration request.

        Args:
            request (Request): The HTTP request object containing user data.

        Returns:
            Response: An HTTP response object. If successful, it contains the new
                      user's data. If not, it contains the validation errors.
        """
        # Instantiate the serializer with the data from the request.
        serializer = RegistrationSerializer(data=request.data)

        data = {}
        # Validate the serializer's data.
        if serializer.is_valid():
            # If valid, save the new user to the database.
            saved_account = serializer.save()
            # Prepare the data to be sent in the response.
            data = {
                "detail": "User created successfully!"
            }
            # Return the user data with a 201_CREATED status.
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            # If the data is invalid, return the errors with a 400 Bad Request status.
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for JWT authentication using Simple JWT.

    This class extends the default TokenObtainPairView to provide login functionality
    with JWT tokens. It overrides the POST method to:
    - Validate user credentials and return access/refresh tokens
    - Set tokens as secure, HTTPOnly cookies for improved security
    - Return a custom response containing user information and a success message

    Usage:
        Send a POST request with username/email and password to this endpoint.
        On success, access and refresh tokens are set as cookies and user info is returned.

    Security:
        - Cookies are set with httponly and secure flags to prevent XSS attacks
        - No tokens are exposed in the response body
    """

    def post(self, request, *args, **kwargs):
        """
        Handles user login and sets JWT tokens as secure cookies.

        This method authenticates the user using credentials from the request data.
        If authentication is successful, it returns a response with:
        - Access and refresh tokens set as HTTPOnly, secure cookies
        - User information in the response body
        - A success message

        Security:
            - Cookies are set with httponly and secure flags to prevent XSS attacks
            - No tokens are exposed in the response body

        Args:
            request (Request): The HTTP request object containing user credentials.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: An HTTP response object with a success message, user info, and cookies set.
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

        # Set the access token in an HTTPOnly cookie.
        # httponly=True: Prevents JavaScript from accessing the cookie.
        # secure=True: Ensures the cookie is only sent over HTTPS.
        # samesite='Lax': Provides a balance between security and usability.
        response.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        # Set the refresh token in an HTTPOnly cookie with the same security settings.
        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        response.status_code = status.HTTP_200_OK

        # Modify the response data to return a success message instead of the tokens.
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
    Custom view to refresh the access token using a refresh token from a cookie.

    This view extends Simple JWT's TokenRefreshView to read the refresh token
    from an HTTPOnly cookie. If the token is valid, it generates a new access
    token and sets it in a new HTTPOnly cookie.
    """

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to refresh an access token.

        Args:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: An HTTP response object with a success message and a new
                      access token cookie, or an error response if the refresh
                      token is missing or invalid.
        """
        # Retrieve the refresh token from the request's cookies.
        refresh_token = request.COOKIES.get("refresh_token")

        # Check if the refresh token exists.
        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Initialize the serializer with the refresh token from the cookie.
        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            # Validate the refresh token. raise_exception=True will raise an exception
            # for invalid tokens.
            serializer.is_valid(raise_exception=True)
        except:
            # If the token is invalid, return an unauthorized status.
            return Response(
                {"detail": "Refresh token invalid!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Get the new access token from the validated serializer data.
        access_token = serializer.validated_data.get("access")

        # Create a response with a success message.
        response = Response({
            "detail": "Token refreshed",
            "access": access_token
        })
        # Set the new access token in a secure, HTTPOnly cookie.
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        return response


class LogoutView(APIView):
    """
    Handles user logout by deleting all tokens and removing cookies.
    POST /api/logout/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        try:
            # Try to blacklist the refresh token if present
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
            # Remove cookies
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response
        except Exception:
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
