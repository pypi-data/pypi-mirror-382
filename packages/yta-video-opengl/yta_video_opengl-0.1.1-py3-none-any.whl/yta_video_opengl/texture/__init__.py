from yta_video_opengl.texture.handler import _GPUTextureHandler
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from dataclasses import dataclass
from typing import Union

import numpy as np
import moderngl


@dataclass
class _OpenGLTextureBinded:
    """
    *For internal use only*

    Texture to use within an OpenGL class, binding
    a location and simplifying the way we handle
    it.
    """

    def __init__(
        self,
        node: '_OpenglNodeBase',
        name: str,
        unit: int,
    ):
        # TODO: I don't know how to validate this...
        #ParameterValidator.validate_subclass_of('node', node, '_OpenglNodeBase')
        """
        We can have 'video.transitions.crossfade.CrossfadeTransitionNode'
        that inherits from '_TransitionNode', that inherits from
        '_OpenglNodeBase' so there is more than one step to
        reach that class...
        """

        self._node: '_OpenglNodeBase' = node
        """
        The parent node instance base this instance
        belongs to
        """
        self.name: str = name
        """
        The name of the uniform associated with this
        texture.
        """
        self.unit: int = unit
        """
        The unit (or location) of this texture within
        the OpenGL context.
        """
        self._handler: _GPUTextureHandler = _GPUTextureHandler(self._node.context)
        """
        The handler of this texture.
        """

        # Assign the unit to the uniform
        self._node.uniforms.set(self.name, self.unit)

    def update(
        self,
        input: Union[moderngl.Texture, np.ndarray] 
    ) -> '_OpenGLTextureBinded':
        """
        Update the content of the texture and set it to be
        used in its unit.
        """
        input = (
            self._handler.update(input)
            if PythonValidator.is_numpy_array(input) else
            input
        )
        input.use(location = self.unit)

        return self

class _Textures:
    """
    *For internal use only*

    Class to wrap the functionality related to
    handling the opengl program textures.
    """

    @property
    def textures(
        self
    ) -> dict:
        """
        The internal dictionary to handle the different
        textures, mapping them by their names.
        """
        if not hasattr(self, '_textures'):
            self._textures = {}

        return self._textures

    def __init__(
        self,
        opengl_node: '_OpenglNodeBase'
    ):
        self._opengl_node: '_OpenglNodeBase' = opengl_node
        """
        The node base instance that is the the parent of
        this instance.
        """
        self.textures # Force creation

    def get(
        self,
        name: str
    ) -> Union[_OpenGLTextureBinded, None]:
        """
        Get the texture with the given 'name'.
        """
        return self.textures.get(name, None)
    
    def add(
        self,
        name: str,
        unit: Union[int, None] = None
    ) -> '_Textures':
        """
        Add a new texture binded to the internal dict.
        """
        unit = (
            len(self.textures)
            if unit is None else
            unit
        )

        self._textures[name] = _OpenGLTextureBinded(
            node = self._opengl_node,
            name = name,
            unit = unit
        )

        return self
    
    def update(
        self,
        name: str,
        input: Union[moderngl.Texture, np.ndarray]
    ) -> '_Textures':
        """
        Update the content of the texture with the given
        'name' by setting the provided 'input' and set
        it to be used in its unit (location).
        """
        self.get(name).update(input)

        return self