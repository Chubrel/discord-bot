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


def try_loop(arg):
    try:
        for _ in arg:
            return True
    except TypeError:
        return False


def try_dict(arg):
    try:
        t = arg.__dict__
    except AttributeError:
        return None
    else:
        return t


objs = []
import _asyncio


def values(arg):
    global objs
    if arg is None or arg in objs:
        return
    else:
        objs.append(arg)
        if isinstance(arg, _asyncio.Task):
            print('lol <<<<<<<<<<<<<<<<<<<<<<<<<<')
    t = try_dict(arg)
    if t is not None:
        values(t)
    elif isinstance(arg, dict):
        for k, v in arg.items():
            if not isinstance(k, str) or not k.startswith('__'):
                values(v)
    else:
        if try_loop(arg):
            for i in arg:
                values(i)
        else:
            print(arg)


# Заканчиваем штуки
def save():
    global data
    with open('data', 'wb') as db:
        pickle.dump(data, db)


if __name__ == '__main__':
    load()
