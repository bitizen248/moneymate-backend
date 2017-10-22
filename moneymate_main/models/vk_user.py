from django.db import models
from django.db.models import Model
from rest_framework import serializers


class VKUser(Model):
    """
    Объеект пользователя связаный с ВКонтакте
    """

    vk_id = models.CharField(max_length=14, unique=True)
    """
    VK ID пользователя
    """

    first_name = models.CharField(max_length=64)
    """
    Имя пользователя
    """

    second_name = models.CharField(max_length=64)
    """
    Фамилия пользователя
    """

    avatar = models.URLField()
    """
    Ссылка на автара пользователя
    """

    vk_token = models.CharField(max_length=64)
    """
    Токен для исользования метод VK
    """

    activated = models.BooleanField(default=False)
    """
    Зарегистрировался ли пользователь в MoneyMate
    """

    local_token = models.CharField(max_length=64, null=True)
    """
    Токен по которому можно идентифицировать пользователя
    """

    def __str__(self):
        return str(self.id) + ": (" + self.first_name + " " + self.second_name + ")"

    class Meta:
        app_label = 'moneymate_main'


class VKUserSerializer(serializers.ModelSerializer):
    """
    Сериализация VKUser в JSON
    ВНИМАНИЕ!!! Серализваоть VKUser можно только с помощью этого класса
    Иначе сервер вернет секретные данные(vk_token, local_token)
    """
    class Meta:
        model = VKUser
        fields = ('id', 'vk_id', 'first_name', 'second_name', 'avatar', 'activated')
