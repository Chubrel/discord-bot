# coding=utf-8
from main import *

client = discord.Client()


def load():
    global data
    try:
        with open('data', 'rb') as db:
            data = pickle.load(db)
    except (FileNotFoundError, pickle.UnpicklingError):
        data = GlobalData()


# Здесь добавляем новые штуки
def add():
    global data


def get_some_data():
    global data
    for k in data.guilds.values():
        print(k.__dict__)
        if isinstance(k, GuildData):
            for member in k.members.values():
                print(1, member.__dict__)
                print(member.tests.ench.__dict__)
        elif isinstance(k, MemberData):
            print(2, k.tests.ench.__dict__)


# Заканчиваем штуки
def save():
    global data
    with open('data', 'wb') as db:
        pickle.dump(data, db)


if __name__ == '__main__':
    load()
