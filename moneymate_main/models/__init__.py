from moneymate_main.models.check import Check, CheckSerializer
from moneymate_main.models.message import Message, MessageSerializer
from moneymate_main.models.room import Room, RoomSerializer
from moneymate_main.models.transaction import Transaction, TransactionsSerializer
from moneymate_main.models.vk_user import VKUser, VKUserSerializer


def getAllModels():
    return VKUser, Room, Check, Transaction, Message
