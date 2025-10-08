from abc import ABC, abstractmethod


class SearchCollectionsAbstract(ABC):
    @abstractmethod
    def search(self, **kwargs):
        raise NotImplementedError()
