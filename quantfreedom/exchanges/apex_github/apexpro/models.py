from collections import namedtuple


def configDecoder(configs):
    return namedtuple('X', configs.keys())(*configs.values())
