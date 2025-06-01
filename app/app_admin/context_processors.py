
from app_auth.models import UserDetails

def user_details(request):
    if request.user.is_authenticated:
        try:
            user_details = UserDetails.objects.get(user=request.user)
            print(user_details)
        except UserDetails.DoesNotExist:
            user_details = None
    else:
        user_details = None
    return {'details': user_details}
