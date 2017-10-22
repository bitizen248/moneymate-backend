from django.db.models import Q
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from moneymate_main.auth import Auth
from moneymate_main.models import Transaction
from moneymate_main.models.transaction import TransactionsSerializer


@api_view(['GET'])
def feed(request):
    """
    Метод требует авторизации
    Принимает параметры
    skip = сколько пропустить
    limit = сколько получить
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
    transactions = Transaction.objects.filter(
        Q(to_user=user)
    ).order_by('created')[skip:limit]
    serial = TransactionsSerializer(transactions, many=True)
    for trans in transactions:
        trans.read = True
        trans.save()
    return JsonResponse(serial.data, safe=False)


@api_view(['GET'])
def getTransactions(request):
    """
    Метод не реализован
    Метод требует авторизации
    Возвращает все транзакции в рамках одного человека или комнаты связаные с пользователем
    """
    pass


@api_view(['POST'])
def createTransaction(request):
    """
    Метод не реализован
    Метод требует авторизации
    Создает транзакции(займ денег, возврат долга)
    """
    pass
