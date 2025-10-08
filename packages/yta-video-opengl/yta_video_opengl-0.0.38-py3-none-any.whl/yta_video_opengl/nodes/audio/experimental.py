from yta_video_opengl.nodes.audio.abstract import _AudioNode
from typing import Union

import numpy as np


class ChorusNode(_AudioNode):
    """
    Apply a chorus effect, also called flanger
    effect.

    TODO: This method is being applied but the
    effect is not being notorious, so it is
    experimental by now.

    TODO: Explain properly
    """

    def __init__(
        self,
        sample_rate: int,
        depth: int = 0,
        frequency: float = 0.25
    ):
        """
        The 'sample_rate' must be the sample rate
        of the audio frame.
        """
        self.sample_rate: int = sample_rate
        self.depth: int = depth
        self.frequency: float = frequency

    def process(
        self,
        input: Union[np.ndarray],
        t: float
    ) -> np.ndarray:
        """
        Process the provided audio 'input' that
        is played on the given 't' time moment.
        """
        n_samples = input.shape[0]
        t = np.arange(n_samples) / self.sample_rate

        # Sinusoidal LFO that controls the delay
        delay = (self.depth / 1000.0) * self.sample_rate * (0.5 * (1 + np.sin(2 * np.pi * self.frequency * t)))
        delay = delay.astype(np.int32)

        output = np.zeros_like(input, dtype=np.float32)

        for i in range(n_samples):
            d = delay[i]

            output[i]= (
                0.7 * input[i] + 0.7 * input[i - d]
                if (i - d) >= 0 else
                input[i]
            )

        return output