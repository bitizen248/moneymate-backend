import requests
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from moneymate_main.auth import Auth


@api_view(['GET'])
def getFriends(request):
    """
    Метод требует авторизации!
    Получения списка друзей из VK
    Параметры
        skip - сколько пропустить от начала
        limit - сколько загрузить
    Возвращает список друзей, подтянутый из ВК, в формате
    {
        "vk_id": (int - id из ВК)
        "first_name": (string - имя),
        "second_name": (string - фамилия),
        "avatar": (string - аватар)
    }
    """
    user = Auth.authenticate(request)
    if not user:
        return Response({
            "success": False,
            "reason": "Permission deny"
        }, status.HTTP_401_UNAUTHORIZED)
    skip = request.query_params.get('skip')
    limit = request.query_params.get('limit')
    if not skip:
        skip = 0
    else:
        skip = int(skip)
    if not limit:
        limit = 20
    else:
        limit = int(limit)
    r = requests.get(settings.VK_METHOD_ROOT + 'friends.get', params={
        'order': 'name',
        'count': limit,
        'offset': skip,
        'fields': 'photo_200',
        'access_token': user.vk_token,
        'v': '5.68'
    })
    res = r.json().get("response").get('items')
    friends = []
    for friend in res:
        friends.append({
            "vk_id": friend.get("id"),
            "first_name": friend.get("first_name"),
            "second_name": friend.get("last_name"),
            "avatar": friend.get("photo_200")
        })
    return Response(friends)
