from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from exchange.models import ExchangeAdmin

## repeated code may move to better place later
def apply_search_filter(queryset, q):
    q = q.strip()
    if not q:
        return queryset

    parts = q.split()
    if len(parts) == 2:
        first, last = parts
        return queryset.filter(
            Q(first_name__icontains=first) & Q(last_name__icontains=last)
        )
    else:
        return queryset.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        )


class AdminExchangeCandidatesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        UserModel = get_user_model()
        admin_usernames = ExchangeAdmin.objects.values_list("username", flat=True)

        users_qs = UserModel.objects.exclude(username__in=admin_usernames).values(
            "id", "username", "first_name", "last_name", "email", "is_active", "date_joined"
        ).order_by('username')

        q = request.GET.get('q', '').strip()
        limit = min(int(request.GET.get('limit', 10)), 100)
        users_qs = apply_search_filter(users_qs, q)

        candidates = []
        for u in users_qs[:limit]:
            u = dict(u)
            u["date_joined"] = str(u.get("date_joined")) if u.get("date_joined") else None
            candidates.append(u)

        return JsonResponse({"candidates": candidates})