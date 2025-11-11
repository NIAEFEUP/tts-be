from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from exchange.models import ExchangeAdmin


class AdminExchangeAdminsView(APIView):
    """Return user info for current exchange admins.

    Requires authentication and is intended to be protected by the
    `exchange_admin_required` middleware when routed.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        UserModel = get_user_model()

        # Get all admin usernames
        admin_usernames = list(ExchangeAdmin.objects.values_list("username", flat=True))

        # Query user rows matching those usernames
        users_qs = UserModel.objects.filter(username__in=admin_usernames).values(
            "id", "username", "first_name", "last_name", "email", "is_active", "date_joined"
        )

        # Minimal serialization: convert date_joined to a string using str()
        admins = []
        for u in users_qs:
            u = dict(u)
            u["date_joined"] = str(u.get("date_joined")) if u.get("date_joined") else None
            admins.append(u)

        return JsonResponse({"admins": admins}, safe=False)

    def post(self, request):
        username = request.data.get('username')
        if not username:
            return JsonResponse({'error': 'Username required'}, status=400)

        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        if ExchangeAdmin.objects.filter(username=username).exists():
            return JsonResponse({'error': 'User is already an admin'}, status=400)

        ExchangeAdmin.objects.create(username=username)
        return JsonResponse({'message': 'Admin added successfully'})

    def delete(self, request, username):
        if not username:
            return JsonResponse({'error': 'Username required'}, status=400)

        deleted, _ = ExchangeAdmin.objects.filter(username=username).delete()
        if deleted == 0:
            return JsonResponse({'error': 'Admin not found'}, status=404)

        return JsonResponse({'message': 'Admin removed successfully'})
