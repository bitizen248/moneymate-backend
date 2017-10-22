import time

from django.db import models
from rest_framework import serializers

from moneymate_main.models.vk_user import VKUserSerializer


class Message(models.Model):
    """
    Объект сообщений внутри комнаты.
    """

    text = models.CharField(max_length=1024)
    """
    Текст сообщения
    """

    room = models.ForeignKey('moneymate_main.Room')
    """
    Объект комнаты
    """

    created = models.DateTimeField(auto_now=True)
    """
    Время создания сообщения
    """

    creator = models.ForeignKey('moneymate_main.VKUser', related_name='+')
    """
    Объект автора сообщения
    """

    read = models.ManyToManyField('moneymate_main.VKUser')
    """
    Массив тех, кто прочитал сообщение
    """

    def getTimestamp(self):
        """
        Метод конвертирует DateTimeField в UNIX Timestamp(в секундах)
        """
        return int(time.mktime(self.created.timetuple()))

    class Meta:
        app_label = 'moneymate_main'


class MessageSerializer(serializers.ModelSerializer):
    """
    Сериализатор объектов Message в JSON
    """
    created = serializers.IntegerField(source='getTimestamp', read_only=True )
    creator = VKUserSerializer()
    read = VKUserSerializer(many=True)

    class Meta:
        model = Message
        exclude = ('created', 'room')
        depth = 1


