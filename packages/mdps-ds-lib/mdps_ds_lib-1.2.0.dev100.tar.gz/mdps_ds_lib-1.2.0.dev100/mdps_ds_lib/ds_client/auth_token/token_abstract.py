from abc import ABC, abstractmethod


class TokenAbstract(ABC):
    @abstractmethod
    def get_token(self):
        return ''
