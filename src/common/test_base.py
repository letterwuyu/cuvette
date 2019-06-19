from abc import ABCMeta, abstractmethod

class TestBase(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(TestBase, self).__init__()

    @abstractmethod
    def initialize(self, options):
        pass

    @abstractmethod
    def run(self):
        pass
