from abc import ABCMeta, abstractmethod

class Wapper(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def get_json_summary(self):
        pass

    @abstractmethod
    def get_txt_summary(self):
        pass
