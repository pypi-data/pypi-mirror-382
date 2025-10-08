"""
Module to include the abstract classes
and avoid import loops.
"""
from abc import ABC, abstractmethod

import numpy as np


class _AudioNode(ABC):
    """
    Base audio node class to implement a
    change in an audio frame by using the
    numpy library.
    """

    @abstractmethod
    def process(
        self,
        input: np.ndarray,
        t: float
    ) -> np.ndarray:
        """
        Process the provided audio 'input' that
        is played on the given 't' time moment.
        """
        pass