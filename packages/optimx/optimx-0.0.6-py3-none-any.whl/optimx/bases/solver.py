from abc import ABC, abstractmethod

class ASolver(ABC):
    
    @abstractmethod
    def solve(self):
        pass