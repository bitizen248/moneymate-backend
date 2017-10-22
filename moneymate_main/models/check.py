import time

from django.db import models
from rest_framework import serializers


class Check(models.Model):
    """
    Объект чека.
    Чеки используются только в комнатах и расчитаны для распределение денег между 2+ людьми
    """

    name = models.CharField(max_length=128)
    """
    Имя чека
    """

    description = models.CharField(max_length=256)
    """
    Описания чека (необязательно поле)
    """

    room = models.ForeignKey('moneymate_main.Room', blank=True)
    """
    Объект связки комнаты и чека(чеки могут быть созданы только в рамках комнаты)
    """

    creator = models.ForeignKey('moneymate_main.VKUser')
    """
    Объект пользователя которй создал чек(он же и платил за этот чек, то есть ему должны все учасники чека)
    """

    created = models.DateTimeField(auto_now=True)
    """
    Время создания чека
    """

    def getTimestamp(self):
        """
        Метод коневртирует DateTimeField в UNIX Timestamp(в секундах)
        """
        return int(time.mktime(self.created.timetuple()))

    def __str__(self):
        return str(self.id) + ":" + self.name

    class Meta:
        app_label = 'moneymate_main'


class CheckSerializer(serializers.ModelSerializer):
    """
    Сериализатор объектов класса Check в JSON
    """

    # creator = VKUserSerializer()
    created = serializers.IntegerField(source='getTimestamp', read_only=True)
    # room = RoomSerializer()

    def __init__(self, *args, **kwargs):
        """
        Расширеный конструктор, реализует поле hide
        Все поля из кортежа hide не будут отображены при конвертировании в JSON
        """

        hide = kwargs.pop('hide', None)

        super(CheckSerializer, self).__init__(*args, **kwargs)

        if hide is not None: # прячем лишнее
            for hide_field in hide:
                self.fields.pop(hide_field)

    class Meta:
        model = Check
        fields = '__all__'
