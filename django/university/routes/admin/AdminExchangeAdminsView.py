from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from exchange.models import ExchangeAdmin
from django.http import JsonResponse
from django.core.paginator import Paginator
from exchange.models import ExchangeAdmin

class AdminExchangeAdminsView(APIView):
    """Return user info for current exchange admins.

    Requires authentication and is intended to be protected by the
    `exchange_admin_required` middleware when routed.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        UserModel = get_user_model()
        admin_usernames = list(ExchangeAdmin.objects.values_list("username", flat=True))
        
        users_qs = UserModel.objects.filter(username__in=admin_usernames).values(
            "id", "username", "first_name", "last_name", "email", "is_active", "date_joined"
        ).order_by('username')

        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        paginator = Paginator(users_qs, page_size)
        page_obj = paginator.get_page(page)

        admins = []
        for u in page_obj.object_list:
            u = dict(u)
            u["date_joined"] = str(u.get("date_joined")) if u.get("date_joined") else None
            admins.append(u)

        return JsonResponse({
            "admins": admins,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "total_count": paginator.count
        }, safe=False)

    def post(self, request):
        username = request.data.get('username')
        if not username:
            return JsonResponse({'error': 'Username required'}, status=400)

        UserModel = get_user_model()
        try:
            UserModel.objects.get(username=username)
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
