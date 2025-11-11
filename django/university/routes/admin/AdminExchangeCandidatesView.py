from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from exchange.models import ExchangeAdmin


class AdminExchangeCandidatesView(APIView):
    """Return all auth users whose username is not present in the ExchangeAdmin table.

    This endpoint requires authentication. It returns a JSON object with a
    `candidates` array containing basic fields for each user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        UserModel = get_user_model()

        admin_usernames = ExchangeAdmin.objects.values_list("username", flat=True)

        users_qs = UserModel.objects.exclude(username__in=admin_usernames).values(
            "id", "username", "first_name", "last_name", "email", "is_active", "date_joined"
        )

        q = request.GET.get('q', '').strip()
        limit = min(int(request.GET.get('limit', 10)), 100)  
        if q:
            users_qs = users_qs.filter(
                models.Q(username__icontains=q) |
                models.Q(first_name__icontains=q) |
                models.Q(last_name__icontains=q) |
                models.Q(email__icontains=q)
            )[:limit]  

        candidates = []
        for u in users_qs:
            u = dict(u)
            u["date_joined"] = str(u.get("date_joined")) if u.get("date_joined") else None
            candidates.append(u)

        return JsonResponse({"candidates": candidates}, safe=False)
