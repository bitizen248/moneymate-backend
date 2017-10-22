import requests
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from moneymate import settings
from moneymate_main.auth import Auth
from moneymate_main.models import VKUserSerializer, VKUser, Room, Message, Transaction
from moneymate_main.models.message import MessageSerializer


@api_view(['GET'])
def lastUpdates(request):
    """
    TODO МЕТОД НЕ ДОДЕЛАН!!!
    Метод требует авторизации
    Возвращает массив последних изменений, которые мог пропустить пользователь
    :return:
    """
    users = VKUser.objects.all()
    rooms = Room.objects.all()
    return Response([
                        {
                            "type": 'user',
                            "avatar": user.avatar,
                            "name": user.first_name
                        } for user in users
                    ] + [
                        {
                            "type": 'room',
                            "avatar": room.avatar,
                            "name": room.name
                        } for room in rooms
                    ])


@api_view(['GET'])
def getRoomsAndUsers(request):
    """
    TODO МЕТОД НЕ ДОДЕЛАН!!!
    Метод требует авторизации!
    Возвращает список всех комнать и пользватель, которые связаны с пользователем
    Сортированы в порядке последней активности
    {
        "type": ("room|user" - тип объекта),
        "id": (int - id объекта),
        "name": (string - имя),
        "avatar": (string - ссылка на аватар)
        "last_message": (string поледня инфа для вывода),
        "last_update": (long timestamp - будет позже)
    }
    """
    user = Auth.authenticate(request)
    if not user:
        return Response({
            "success": False,
            "reason": "Permission deny"
        }, status.HTTP_401_UNAUTHORIZED)
    rooms = Room.objects.filter(users=user)
    users = VKUser.objects.all()
    return Response([
                        {
                            "id": room.id,
                            "type": "room",
                            "name": room.name,
                            "avatar": room.avatar,
                            "last_message": "Последнее сообщение",
                        } for room in rooms
                    ] + [
                        {
                            "id": user.id,
                            "vk_id": user.vk_id,
                            "type": "user",
                            "name": user.first_name  + " " + user.second_name,
                            "avatar": user.avatar,
                            "last_message": "Последнее сообщение"
                        } for user in users
                    ])


@api_view(['GET'])
def search():
    """
    Метод не реализован
    Метод требует авторизации
    Посик по комнатам и пользвателям
    """
    pass


@api_view(['POST'])
def createRoom(request):
    """
    Метод требует авторизации!
    Метод создании комнаты
    Принимает
    {
        "avatar": (string - ссылка на аватар - не реализван метод заливки),
        "name": (string - имя группы),
        "users": [массив id поьзователей из вк]
    }
    Возвращает:
    {
        "success": (bool)
        "reason": (string - если что-то пойдет не так, возвращает причину)
        "room_id": (int - id новой комнаты)
    }
    :param request:
    :return:
    """
    user = Auth.authenticate(request)
    if not user:
        return Response({
            "success": False,
            "reason": "Permission deny"
        }, status.HTTP_401_UNAUTHORIZED)
    if not request.data.get('name'):
        return Response({
            "success": False,
            "reason": "Не указано имя"
        }, status.HTTP_400_BAD_REQUEST)
    users_ids = set(request.data.get('users'))
    if user.vk_id not in users_ids:
        users_ids.add(user.vk_id)
    if not request.data.get('users') or len(users_ids) < 3:
        return Response({
            "success": False,
            "reason": "Не корректный список пользователей"
        }, status.HTTP_400_BAD_REQUEST)
    new_room = Room()
    new_room.name = request.data.get('name')
    if request.data.get('avatar'):
        new_room.avatar = request.data.get('avatar')
    new_room.save()
    r = requests.get(settings.VK_METHOD_ROOT + 'users.get', params={
        'user_ids': ",".join(str(vk_id) for vk_id in users_ids),
        'access_token': user.vk_token,
        'fields': 'photo_200',
        'v': '5.68'
    })
    users = []
    for user_info in r.json().get("response"):
        if VKUser.objects.filter(vk_id=user_info.get('id')).count() > 0:
            user = VKUser.objects.get(vk_id=user_info.get('id'))
        else:
            user = VKUser(vk_id=user_info.get('id'))
            user.activated = False
        user.first_name = user_info.get('first_name')
        user.second_name = user_info.get('last_name')
        user.avatar = user_info.get('photo_200')
        user.save()
        users.append(user)
    print(users)
    new_room.users.add(*users)
    new_room.save()
    return Response({
        "success": True,
        "room_id": new_room.id
    })


@api_view(['POST'])
def startWithUser():
    """
    Метод не реализован
    Метод требует авторизации
    Метод должен собрать данные из ВК по пользователю и вернуть все данные,
    необходимые для начально работы деатльного экрана
    """
    pass


@api_view(['GET'])
def getMessages(request):
    """
    Метод требует авторизации!
    Получение сообзений в комнате
    Принемаемые параметры
    skip
    limit
    room_id - id комнаты
    """
    user = Auth.authenticate(request)
    if not user:
        return Response({
            "success": False,
            "reason": "Permission deny"
        }, status.HTTP_401_UNAUTHORIZED)
    skip = request.query_params.get('skip')
    limit = request.query_params.get('limit')
    room_id = request.query_params.get('room_id')
    if not room_id:
        return Response({
            "success": False,
            "reason": "Не указана комната"
        })
    if not skip:
        skip = 0
    else:
        skip = int(skip)
    if not limit:
        limit = 20
    else:
        limit = int(limit)
    if not Room.objects.filter(id=room_id).exists():
        return Response({
            "success": False,
            "reason": "Комната не существует"
        })
    room = Room.objects.get(id=room_id)
    messages = Message.objects.filter(room=room).order_by('created')[skip:limit]
    serial = MessageSerializer(messages, many=True)
    for message in messages:
        if user not in message.read.all():
            message.read.add(user)
            message.save()
    return JsonResponse(serial.data, safe=False)


@api_view(['POST'])
def sendMessage(request):
    """
    Метод требует авторизации
    Отправка сообщения в комнату
    На вход получаем объект
    {
        "text": (string - текст сообщения),
        "room": (int - id комнаты)
    }
    """
    user = Auth.authenticate(request)
    if not user:
        return Response({
            "success": False,
            "reason": "Permission deny"
        }, status.HTTP_401_UNAUTHORIZED)
    new_message = Message()
    if not request.data.get('text') or not request.data.get('text').strip():
        return Response({
            "success": False,
            "reason": "Не указан текст сообщения"
        }, status.HTTP_400_BAD_REQUEST)
    new_message.text = request.data.get('text').strip()
    if not request.data.get('room'):
        return Response({
            "success": False,
            "reason": "Комната не указана"
        }, status.HTTP_400_BAD_REQUEST)
    if not Room.objects.filter(id=request.data.get('room')).exists():
        return Response({
            "success": False,
            "reason": "Такая комната не существует"
        }, status.HTTP_400_BAD_REQUEST)
    room = Room.objects.get(id=request.data.get('room'))
    if user not in room.users.all():
        return Response({
            "success": False,
            "reason": "Вы не состоите в это комнате"
        }, status.HTTP_400_BAD_REQUEST)
    new_message.creator = user
    new_message.room = room
    new_message.save()
    new_message.read.add(user)
    new_message.save()
    return Response({
        "success": True
    })


@api_view(['GET'])
def getUsers(request):
    """
    Получения списка пользователей в комнате + общий долг пользователя другому пользователю
    Принимает:
    room_id - id комнаты
    Отдает:
    [{
        "user": (object - объект пользователя),
        "total_amount": (float - ссымарный долг пользователю в рамках этой комнаты)
    },...]
    """
    user = Auth.authenticate(request)
    if not user:
        return Response({
            "success": False,
            "reason": "Permission deny"
        }, status.HTTP_401_UNAUTHORIZED)
    if not request.query_params.get('room_id'):
        return Response({
            "success": False,
            "reason": "Не указан номер комнаты"
        }, status.HTTP_400_BAD_REQUEST)
    if not Room.objects.filter(id=request.query_params.get('room_id')).exists():
        return Response({
            "success": False,
            "reason": "Указанной комнаты не существует"
        }, status.HTTP_400_BAD_REQUEST)
    room = Room.objects.get(id=request.query_params.get('room_id'))
    if user not in room.users.all():
        return Response({
            "success": False,
            "reason": "Вы не состоите в данной комнате"
        }, status.HTTP_403_FORBIDDEN)
    res = []
    users_in_room = list(room.users.all())
    users_in_room.remove(user)
    for room_user in users_in_room:
        user_room_info = dict()
        user_room_info['user'] = VKUserSerializer(room_user).data
        total = 0.0
        to_user = Transaction.objects.filter(from_user_id=user.id, to_user_id=room_user.id, room=room)
        for tr in to_user:
            total += tr.amount
        from_user = Transaction.objects.filter(from_user_id=room_user.id, to_user_id=user.id, room=room)
        for tr in from_user:
            total -= tr.amount
        user_room_info['total_amount'] = total
        res.append(user_room_info)
    return Response(res)


@api_view(['POST'])
def addUser():
    """
    Метод не реализован
    Метод требует авторизации
    Добавление пользователя в комнату
    """
    pass


@api_view(['POST'])
def removeUser():
    """
    Метод не реализован
    Метод требует авторизации
    Удалени пользователя из комнаты
    """
    pass


@api_view(['POST'])
def changeName():
    """
    Метод не реализован
    Метод требует авторизации
    Изменение названия комнаты
    """
    pass
