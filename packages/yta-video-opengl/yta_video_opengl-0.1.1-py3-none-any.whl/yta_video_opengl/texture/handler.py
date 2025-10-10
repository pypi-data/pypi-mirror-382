from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from typing import Union

import numpy as np
import moderngl


class _GPUTextureHandler:
    """
    *For internal use only*
    
    A texture handler that is used to handle video frames
    that have been loaded from CPU (probably by reading
    from a video file) and are converted to an OpenGL
    texture in the most efficient way.
    """

    def __init__(
        self,
        opengl_context: Union[moderngl.Context, None],
    ):
        ParameterValidator.validate_instance_of('opengl_context', opengl_context, moderngl.Context)

        self.opengl_context: moderngl.Context = (
            moderngl.create_context(standalone = True)
            if opengl_context is None else
            opengl_context
        )
        """
        The context of the OpenGL program.
        """
        self.texture = None
        """
        The OpenGL texture.
        """
    
    def update(
        self,
        frame: Union[moderngl.Texture, np.ndarray]
    ) -> moderngl.Texture:
        """
        Update the texture object content with the 'frame'
        provided, that is a numpy array that will be flipped
        and adapted.

        (!) Do not do 'flipud' before passing the parameter,
        if you read it from a video file, because this 'update'
        method will do it.
        """
        if PythonValidator.is_instance_of(frame, moderngl.Texture):
            return frame
        
        frame = _prepare_frame_to_texture(frame)

        h, w, c = frame.shape

        # Create or update texture if needed (different
        # size or number of channels)
        if (
            self.texture is None
            or self._last_shape != (h, w)
            or self._last_components != c
        ):
            self.texture = self.opengl_context.texture(
                size = (w, h),
                components = c,
                # Empty texture by now
                data = None
            )
            # If we want to repeat or to let it be black pixels
            self.texture.repeat_x = False
            self.texture.repeat_y = False
            self.texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

            self._last_shape = (h, w)
            self._last_components = c

        # Rewrite the frame as a texture
        self.texture.write(frame.tobytes())

        return self.texture
    
def _prepare_frame_to_texture(
    frame: Union[moderngl.Texture, np.ndarray]
) -> np.ndarray:
    """
    *For internal use only*

    Prepare a raw video numpy frame to be used as
    a texture by flipping it (the y axis) and 
    forcing the 'np.uint8' if needed.
    """
    # Invert vertically for OpenGL
    frame = np.flipud(frame)

    return (
        # Force 'np.uint8' format
        np.clip(frame, 0, 255).astype(np.uint8)
        if frame.dtype != np.uint8 else
        frame
    )