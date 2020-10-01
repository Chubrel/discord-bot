# coding=utf-8
import discord
import pickle

client = discord.Client()

try:
    with open('data', 'rb') as db:
        homes, active_games = pickle.load(db)
except (FileNotFoundError, pickle.UnpicklingError):
    homes = {}
    active_games = {}

# Здесь добавляем новые штуки



# Заканчиваем штуки

with open('data', 'wb') as db:
    pickle.dump((homes, active_games), db)
