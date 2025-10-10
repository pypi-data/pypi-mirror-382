"""
Module to include the abstract classes
and avoid import loops.
"""
from typing import Union
from abc import ABC, abstractmethod

import moderngl


class _VideoNode(ABC):
    """
    Base abstract class to represent a video
    node, which is an entity that processes
    video frames individually.

    This class must be inherited by any video
    node class.
    """

    # TODO: What about the types?
    # TODO: Should we expect pyav frames (?)
    @abstractmethod
    def process(
        self,
        frame: Union['VideoFrame', moderngl.Texture, 'np.ndarray'],
        t: float
        # TODO: Maybe we need 'fps' and 'number_of_frames'
        # to calculate progressions or similar...
    ) -> Union['VideoFrame', moderngl.Texture, 'np.ndarray']:
        pass