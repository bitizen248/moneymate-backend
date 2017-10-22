from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from moneymate_main.auth import Auth
from moneymate_main.models import Check, Room, VKUser, Transaction, CheckSerializer, TransactionsSerializer


@api_view(['GET'])
def getCheck(request):
    """
    Метод требует авторизации
    Получени информации по чеку
    На вход
    check_id - id чека
    Возвращает
    {
        "check_info": (object - инфа то чеку)
        "transactions": [(object - транзакции связанне с чеком)]
    }
    """
    user = Auth.authenticate(request)
    if not user:
        return Response({
            "success": False,
            "reason": "Permission deny"
        }, status.HTTP_401_UNAUTHORIZED)
    if not request.query_params.get('check_id'):
        return Response({
            "success": False,
            "reason": "Не указан id чека"
        }, status.HTTP_400_BAD_REQUEST)
    if not Check.objects.filter(id=request.query_params.get('check_id')).exists():
        return Response({
            "success": False,
            "reason": "Такого чека не существует"
        }, status.HTTP_400_BAD_REQUEST)
    check = Check.objects.get(id=request.query_params.get('check_id'))
    room = check.room
    if user not in list(room.users.all()):
        return Response({
            "success": False,
            "reason": "Вы не состоите в комнате, которой приналежит чек"
        }, status.HTTP_403_FORBIDDEN)
    transactions = Transaction.objects.filter(related_check=check)
    return Response({
        "check_info": CheckSerializer(check, hide=('room',)).data,
        "transactions": TransactionsSerializer(transactions, many=True, hide=('related_check', 'room', 'type', 'read',
                                                                              'created', 'from_user')).data
    })


@api_view(['POST'])
def createCheck(request):
    """
    Метод требует авторизации!
    Метод по созанию чека
    Метод принимает:
    {
        "name": (string - имя чека)
        "description": (string(Необязательно) - описание чека)
        "room": (int - id комнаты)
        "users": [{
            "user_id": (int - id пользователя, локальный)
            "amount": (float - сколько ты за него заплатил)
        },...]
    }
    """
    user = Auth.authenticate(request)
    if not user:
        return Response({
            "success": False,
            "reason": "Permission deny"
        }, status.HTTP_401_UNAUTHORIZED)
    new_check = Check()
    if not request.data.get('name'):
        return Response({
            "success": False,
            "reason": "Не указано имя"
        }, status.HTTP_400_BAD_REQUEST)
    new_check.name = request.data.get('name')
    if request.data.get('description'):
        new_check.description = request.data.get('description')
    if not Room.objects.filter(id=request.data.get('room')).exists():
        return Response({
            "success": False,
            "reason": "Комната не существует"
        }, status.HTTP_400_BAD_REQUEST)
    room = Room.objects.get(id=request.data.get('room'))
    new_check.room = room
    new_check.creator = user
    if not request.data.get('users'):
        return Response({
            "success": False,
            "reason": "Пользоавтели не указаны"
        }, status.HTTP_400_BAD_REQUEST)
    users_short = request.data.get('users')
    users = dict()
    for user_short in users_short:
        if user_short.get('amount') > 0 and user_short.get('user_id') != user.id:
            user_buf = VKUser.objects.get(id=user_short.get('user_id'))
            users[user_buf] = user_short.get('amount')
    if not set(list(users.keys())).issubset(set(room.users.all())):
        return Response({
            "success": False,
            "reason": "Один из пользователей не состоит в указаной комнате"
        }, status.HTTP_400_BAD_REQUEST)
    new_check.save()
    for user_trans in users.keys():
        transaction = Transaction()
        transaction.room = room
        transaction.from_user = user
        transaction.to_user = user_trans
        transaction.amount = users.get(user_trans)
        transaction.related_check = new_check
        transaction.name = new_check.name
        if new_check.description:
            transaction.description = new_check.description
        transaction.confirmed = True
        transaction.type = 'check'
        transaction.save()

    return Response({
        "success": True,
        "check_id": new_check.id
    })


@api_view(['POST'])
def deleteCheck(request):
    """
    Для метода требуется авторизация
    Удаление чека
    Параметры на вход
    check_id - id чека
    """
    user = Auth.authenticate(request)
    if not user:
        return Response({
            "success": False,
            "reason": "Permission deny"
        }, status.HTTP_401_UNAUTHORIZED)
    if not request.query_params.get('check_id'):
        return Response({
            "success": False,
            "reason": "Не указан id чека"
        }, status.HTTP_400_BAD_REQUEST)
    if not Check.objects.filter(id=request.query_params.get('check_id')).exists():
        return Response({
            "success": False,
            "reason": "Такого чека не существует"
        }, status.HTTP_400_BAD_REQUEST)
    check = Check.objects.get(id=request.query_params.get('check_id'))
    room = check.room
    if user not in list(room.users.all()):
        return Response({
            "success": False,
            "reason": "Вы не состоите в комнате, которой приналежит чек"
        }, status.HTTP_403_FORBIDDEN)
    check.delete()
    return Response({
        "success": True
    })
