import random
import string

import requests
from django.conf import settings
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from moneymate_main.models import VKUser


class VkRegistration(APIView):
    """
    Метод для регитсрации
    Если GET - возвразает
    {
        "url": (string - по этому URL входим в вк, и ждем перехода на https://oauth.vk.com/blank.html,
        в параметрах прийдет code, выслать его сюда же через POST)
    }
    Если POST - отправляем
    {
        "code": (string - code от VK)
    }
    В ответ получаем
    {
        "success": True
        "token": (sting - token, по которому ходим на сервер, прикреплять в header TOKEN)
    }
    """
    parser_classes = (JSONParser,)
    redirect_url = "https://oauth.vk.com/blank.html"

    def get(self, request, format=None):
        return Response({
            "url": "https://oauth.vk.com/authorize?client_id=" + settings.VK_APP_ID + "display=mobile&redirect_uri=" + self.redirect_url + "&scope=offline&response_type=code&v=5.68"
        })

    def post(self, request, format=None):
        if request.data.get('code'):
            code = request.data.get('code')
            r = requests.get('https://oauth.vk.com/access_token', params={
                'client_id': settings.VK_APP_ID,
                'client_secret': settings.VK_APP_SECRET,
                'redirect_uri': self.redirect_url,
                'code': code
            })
            if r.status_code == 200:
                res = r.json()
                token = res.get('access_token')
                user_id = str(res.get('user_id'))
                r = requests.get(settings.VK_METHOD_ROOT + 'users.get', params={
                    'user_ids': user_id,
                    'access_token': token,
                    'fields': 'photo_200',
                    'v': '5.68'
                })
                user_info = r.json().get("response")[0]
                if VKUser.objects.filter(vk_id=user_id).count() > 0:
                    user = VKUser.objects.get(vk_id=user_id)
                else:
                    user = VKUser(vk_id=user_id)
                user.first_name = user_info.get('first_name')
                user.second_name = user_info.get('last_name')
                user.avatar = user_info.get('photo_200')
                user.vk_token = token
                user.activated = True
                user.local_token = ''.join(
                    random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(24))
                user.save()
                return Response({
                    'success': True,
                    'token': user.local_token
                })
            else:
                res = r.json()
                return Response({
                    'success': False,
                    'code': 'Не удалсь завершить регитсрацию. Повторите попытку'
                })
        else:
            return Response({
                'success': False,
                'reason': 'No token'
            }, status=status.HTTP_400_BAD_REQUEST)
