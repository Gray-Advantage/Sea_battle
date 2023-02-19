from json import load, dump
from os import path
import constants

SETTINGS = {}


def init():
    global SETTINGS
    if not path.exists(constants.SETTINGS_FILE_NAME):
        save_changes(constants.DEFAULT_SETTINGS)
    with open(constants.SETTINGS_FILE_NAME) as settings_file:
        SETTINGS = load(settings_file)


def save_changes(settings_dict):
    with open(constants.SETTINGS_FILE_NAME, 'w') as settings_file:
        dump(settings_dict, settings_file)


def set_option(key, value):
    SETTINGS[key] = value
    save_changes(SETTINGS)


init()
