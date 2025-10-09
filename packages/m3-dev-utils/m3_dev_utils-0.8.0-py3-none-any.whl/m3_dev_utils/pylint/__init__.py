# coding: utf-8
from .m3 import M3Checker


def register(linter):
    linter.register_checker(M3Checker(linter))
