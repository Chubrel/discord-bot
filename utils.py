#! python
# coding=utf-8


import json
import logging
import pickle


DATA = 'data'
GAME_VERISON = '1.16'

CANNOT_READ = "Can't read data from '{}'"
FILE_NOT_FOUND = "File not found: '{}'"

LANG_LIST = ('ru_ru', 'en_us')


class GlobalData:
    pass


class Loaders:

    @classmethod
    def set_logging(cls, *, debug: bool):
        if debug:
            log = logging.DEBUG
        else:
            log = logging.WARN

        logger = logging.getLogger('discord')
        logger.setLevel(log)
        handler = logging.FileHandler(filename='utils/discord.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        logger.addHandler(handler)

    @classmethod
    def load_data(cls) -> GlobalData:
        try:
            with open(DATA, 'rb') as db:
                data = pickle.load(db)
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            print(CANNOT_READ.format(DATA))
            data = GlobalData()
        return data

    @classmethod
    def save_data(cls, data) -> None:
        try:
            with open(DATA, 'wb') as db:
                pickle.dump(data, db)
        except TypeError as error:
            print(error)

    @classmethod
    def read_file(cls, file_name: str) -> str:
        with open(file_name, 'r', encoding='UTF-8') as file:
            return file.read()

    @classmethod
    def load_json(cls, path: str) -> dict:
        try:
            with open(path + '.json', encoding='utf-8') as lang_file:
                return json.load(lang_file)
        except (FileNotFoundError, json.JSONDecodeError):
            raise ValueError(CANNOT_READ.format(f'langs/{path}.json'))

    @classmethod
    def load_lang(cls, name: str) -> dict:
        return Loaders.load_json('langs/' + name)

    @classmethod
    def load_ench_data(cls) -> dict:
        return Loaders.load_json('activities/ench/' + GAME_VERISON)

    @classmethod
    def load_guess_data(cls) -> dict:
        return Loaders.load_json('activities/guess/' + GAME_VERISON)

    @classmethod
    def load_langs(cls) -> dict:
        lang_dict = {}
        for elem in LANG_LIST:
            lang_dict[elem] = Loaders.load_lang(elem)
        return lang_dict
