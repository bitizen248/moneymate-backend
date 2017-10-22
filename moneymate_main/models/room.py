from django.db import models
from rest_framework import serializers

from moneymate_main.models import VKUserSerializer


class Room(models.Model):
    """
    Объект комнаты
    Комната объединяет нескольких людей в единую группу,
    что позволяет распределять деньги и делать объявления в виде сообщений(Message)
    """

    name = models.CharField(max_length=128)
    """
    Имя комнаты
    """

    avatar = models.URLField(blank=True)
    """
    Ссылка на автар комнаты
    """

    creator = models.ForeignKey('moneymate_main.VKUser', related_name='+')
    """
    Создатель комнаты(он же и администратор)
    """

    users = models.ManyToManyField('moneymate_main.VKUser')
    """
    Пользователи, состоящие в комнате
    """

    def __str__(self):
        return str(self.id) + ":" + self.name

    class Meta:
        app_label = 'moneymate_main'


class RoomSerializer(serializers.ModelSerializer):
    """
    Сериализатор объектов Room в JSON
    """

    creator = VKUserSerializer()
    users = VKUserSerializer(many=True)

    class Meta:
        model = Room
        fields = '__all__'
