import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header


class ServiceUser(AnonymousUser):
    def __init__(self, user_id):
        super().__init__()
        self.id = user_id

    @property
    def is_authenticated(self):
        return True


class ServiceJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b"bearer":
            return None

        if len(auth) != 2:
            raise exceptions.AuthenticationFailed("Invalid Authorization header.")

        token = auth[1].decode("utf-8")
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SHARED_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        except jwt.InvalidTokenError as exc:
            raise exceptions.AuthenticationFailed("Invalid token.") from exc

        user_id = payload.get("user_id")
        if not user_id:
            raise exceptions.AuthenticationFailed("Token missing user_id.")

        return (ServiceUser(user_id), payload)