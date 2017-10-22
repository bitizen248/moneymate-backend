import time

from django.db import models
from rest_framework import serializers

from moneymate_main.models import VKUserSerializer, RoomSerializer


class Transaction(models.Model):
    """
    Модель транзакции
    Транзакции - это факт займа/возврата денег другому пользователю
    """

    related_check = models.ForeignKey('moneymate_main.Check', null=True, blank=True)
    """
    В рамках какого чека происходит транзакция(если относиться к комнате чеку)
    """

    name = models.CharField(max_length=64, blank=False)
    """
    Имя чека
    """

    description = models.CharField(max_length=256, blank=True)
    """
    Небольшое описание чека
    """

    room = models.ForeignKey('moneymate_main.Room', null=True, blank=True)
    """
    В рамках какой комнаты проходит транзакиция(если относиться к комнате)
    """

    from_user = models.ForeignKey('moneymate_main.VKUser', related_name='from+')
    """
    Пользователь который отдолжил денег
    """

    to_user = models.ForeignKey('moneymate_main.VKUser')
    """
    Пользователь, который взял в долг
    """

    amount = models.FloatField()
    """
    Занимаемая сумма
    """

    confirmed = models.BooleanField(default=True)
    """
    Потверждил ли пользователь возврат денег(для типов personal и rom)
    """
    type = models.CharField(max_length=16, blank=False, choices=(
        ('personal', 'Personal'),
        ('check', 'Check'),
        ('room', 'Room')
    ))

    created = models.DateTimeField(auto_now=True)
    """
    Время создания транзакции
    """

    read = models.BooleanField(default=False)
    """
    Уведил ли получатель транзакцию
    """

    def getTimestamp(self):
        """
        Метод конвертирует DateTimeField в UNIX Timestamp(в секундах)
        """
        return int(time.mktime(self.created.timetuple()))

    def __str__(self):
        return str(self.id) + ":" + self.name

    class Meta:
        app_label = 'moneymate_main'


class TransactionsSerializer(serializers.ModelSerializer):
    """
    Сериализатор Transaction в JSON
    """

    created = serializers.IntegerField(source='getTimestamp', read_only=True )
    from_user = VKUserSerializer()
    to_user = VKUserSerializer()
    room = RoomSerializer()

    def __init__(self, *args, **kwargs):
        hide = kwargs.pop('hide', None)

        super(TransactionsSerializer, self).__init__(*args, **kwargs)

        if hide is not None:
            for hide_field in hide:
                self.fields.pop(hide_field)

    class Meta:
        model = Transaction
        exclude = ('created',)
        depth = 2
