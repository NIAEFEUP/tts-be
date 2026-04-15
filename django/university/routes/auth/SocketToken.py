from django.http import JsonResponse
from django.views import View
import jwt
import datetime

from tts_be.settings import JWT_KEY, DEBUG


class SocketToken(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Not authenticated"}, status=401)

        expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            hours=12
        )

        token = jwt.encode(
            {"username": request.user.username, "exp": expiration.timestamp()},
            JWT_KEY,
            algorithm="HS256",
        )

        return JsonResponse({"token": token})
