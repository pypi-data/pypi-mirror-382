from abc import ABC, abstractmethod


class SearchGranulesAbstract(ABC):
    @abstractmethod
    def search(self, **kwargs) -> list:
        raise NotImplementedError()
