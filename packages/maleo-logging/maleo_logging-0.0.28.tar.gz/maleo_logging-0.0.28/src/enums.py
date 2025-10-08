import logging
from enum import IntEnum, StrEnum
from maleo.types.integer import ListOfIntegers
from maleo.types.string import ListOfStrings


class Level(IntEnum):
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARN
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

    @classmethod
    def choices(cls) -> ListOfIntegers:
        return [e.value for e in cls]


class LoggerType(StrEnum):
    BASE = "base"
    APPLICATION = "application"
    CACHE = "cache"
    CLIENT = "client"
    CONTROLLER = "controller"
    DATABASE = "database"
    EXCEPTION = "exception"
    MIDDLEWARE = "middleware"
    REPOSITORY = "repository"
    SERVICE = "service"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]
