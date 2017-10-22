from rest_framework import exceptions

from moneymate_main.models import VKUser


class Auth:
    """
    Класс по работе с опознованием пользователем
    """
    @staticmethod
    def authenticate(request):
        token = request.META.get('HTTP_TOKEN')
        if not token:
            return None
        else:
            try:
                user = VKUser.objects.get(local_token=token)
            except VKUser.DoesNotExist:
                raise exceptions.AuthenticationFailed('No such user')
            return user
