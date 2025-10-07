"""
TODO: Note for the developer.

Check the '.gsls' files and make sure the 
variables fit the expected variables:
- `in_pos` must be renamed to `in_vert`
- `in_uv` must be renamed to `in_texcoord`

The textures should be called `texA` and
`texB`.
"""
from yta_video_opengl.nodes.video.opengl import OpenglNodeBase
from yta_video_opengl.decorators import force_inputs_as_textures
from typing import Union
from abc import abstractmethod

import moderngl


class _TransitionNode(OpenglNodeBase):
    """
    *For internal use only*
    
    Base Transition Node to be inherited by
    the transitions we create that handle 2
    different textures.

    These are the variable names of the 
    textures within the '.gsls' code:
    - `textA` - The texture of the first clip
    - `textB` - The texture of the second clip
    """

    @property
    @abstractmethod
    def vertex_shader(
        self
    ) -> str:
        """
        The code of the vertex shader.
        """
        pass

    @property
    @abstractmethod
    def fragment_shader(
        self
    ) -> str:
        """
        The code of the fragment shader.
        """
        pass

    @force_inputs_as_textures
    def process(
        self,
        input_a: Union[moderngl.Texture, 'np.ndarray'],
        input_b: Union[moderngl.Texture, 'np.ndarray'],
        progress: float,
        **kwargs
        # TODO: Maybe I need something else (?)
    ) -> moderngl.Texture:
        """
        Process the 2 frames and get the result texture.
        """
        self.fbo.use()
        self.context.clear(0.0, 0.0, 0.0, 0.0)

        # Bind the textures of the 2 clip frames
        input_a.use(location = 0)
        self.program['texA'] = 0
        input_b.use(location = 1)
        self.program['texB'] = 1

        # Set 'progress' to handle the transition progress
        if 'progress' in self.program:
            self.program['progress'].value = progress

        # Set any existing uniform dynamically
        for key, value in kwargs.items():
            self.uniforms.set(key, value)

        self.quad.render()

        return self.output_tex