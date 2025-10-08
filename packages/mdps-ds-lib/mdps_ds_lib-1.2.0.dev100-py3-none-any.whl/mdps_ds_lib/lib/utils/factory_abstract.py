from abc import ABC, abstractmethod


class FactoryAbstract(ABC):
    @abstractmethod
    def get_instance(self, class_type, **kwargs):
        return

    @abstractmethod
    def get_instance_from_env(self, **kwargs):
        return
