from moneymate_main.models.check import Check
from moneymate_main.models.message import Message
from moneymate_main.models.room import Room
from moneymate_main.models.transaction import Transaction
from moneymate_main.models.vk_user import VKUser


def getAllModels():
    return VKUser, Room, Check, Transaction, Message
