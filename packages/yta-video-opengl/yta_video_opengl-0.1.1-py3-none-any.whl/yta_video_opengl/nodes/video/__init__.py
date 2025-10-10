"""
Interesting information:
| Abrev.  | Nombre completo            | Uso principal                          |
| ------- | -------------------------- | -------------------------------------- |
| VAO     | Vertex Array Object        | Esquema de datos de vértices           |
| VBO     | Vertex Buffer Object       | Datos crudos de vértices en GPU        |
| FBO     | Frame Buffer Object        | Renderizar fuera de pantalla           |
| UBO     | Uniform Buffer Object      | Variables `uniform` compartidas        |
| EBO/IBO | Element / Index Buffer Obj | Índices para reutilizar vértices       |
| PBO     | Pixel Buffer Object        | Transferencia rápida de imágenes       |
| RBO     | Render Buffer Object       | Almacén intermedio (profundidad, etc.) |
"""
from yta_video_opengl.texture import _Textures
from yta_video_opengl.uniforms import _Uniforms
from yta_video_opengl.utils import get_fullscreen_quad_vao
from yta_video_opengl.nodes.video.abstract import _VideoNode
from yta_validation.parameter import ParameterValidator
from abc import abstractmethod
from typing import Union

import numpy as np
import moderngl


class _OpenglNodeBase(_VideoNode):
    """
    The basic class of a node to manipulate frames
    as opengl textures. This node will process the
    frame as an input texture and will generate 
    also a texture as the output.

    Nodes can be chained and the result from one
    node can be applied on another node.

    The texture variable must be `tex`.
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

    def __init__(
        self,
        opengl_context: Union[moderngl.Context, None],
        size: tuple[int, int],
        **kwargs
    ):
        ParameterValidator.validate_instance_of('opengl_context', opengl_context, moderngl.Context)
        # TODO: Validate size

        self.context: moderngl.Context = (
            moderngl.create_context(standalone = True)
            if opengl_context is None else
            opengl_context
        )
        """
        The context of the OpenGL program.
        """
        self.size: tuple[int, int] = size
        """
        The size we want to use for the frame buffer
        in a (width, height) format.
        """
        # Compile shaders within the program
        self.program: moderngl.Program = self.context.program(
            vertex_shader = self.vertex_shader,
            fragment_shader = self.fragment_shader
        )

        # Create the fullscreen quad
        self.quad = get_fullscreen_quad_vao(
            context = self.context,
            program = self.program
        )

        self.uniforms: _Uniforms = _Uniforms(self.program)
        """
        Shortcut to the uniforms functionality.
        """
        self.textures: _Textures = _Textures(self)
        """
        Shortcut to the internal textures handler instance.
        """

        # Prepare textures
        self._prepare_output_texture(self.size)
        self._prepare_input_textures()

        """
        Here we set the uniforms dynamically, that are the
        initial uniforms and would be static during the
        whole rendering process. You can set or update the
        uniforms also when processing each frame if needed.

        We can define an effect with a specific parameter
        that is set here, but we can pass a dynamic `t` or
        a random value to process each frame.
        """
        for key, value in kwargs.items():
            self.uniforms.set(key, value)

    # TODO: Overwrite this method
    def _prepare_input_textures(
        self
    ) -> '_OpenglNodeBase':
        """
        *For internal use only*

        *This method must be overwritten*

        Set the input texture variables and handlers
        we need to manage this.
        """
        self.textures.add('tex', 0)

        return self

    def _prepare_output_texture(
        self,
        size: tuple[int, int]
    ) -> '_OpenglNodeBase':
        """
        *For internal use only*

        Set the output texture and the FBO if needed
        (the size changed or it was not set). This
        method has to be called before rendering any
        frame/texture to adapt it if needed.

        The output texture settings and the FBO will
        determine how the output result is obtained.
        """
        if (
            not hasattr(self, '_output_tex') or
            self._output_tex is None or
            self._output_tex.size != size
        ):
            self._output_tex = self.context.texture(self.size, 4)
            self._output_tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
            # Avoid repeating the texture and use black pixels instead
            # self._output_tex.repeat_x = False
            # self._output_tex.repeat_y = False
            self.fbo = self.context.framebuffer(color_attachments = [self._output_tex])

        return self

    def _process_common(
        self,
        textures_map: dict,
        **kwargs
    ) -> moderngl.Texture:
        """
        *For internal use only*

        Common and internal method to process the inputs
        and obtain the result.

        The `textures_map` is a dict to map the input
        frames to the textures, and it has to include the
        uniform texture name as the key and the method
        parameter as the value:
        - `{'texA': tex_a, 'texB': tex_b}`
        """
        if not textures_map:
            raise ValueError('At least one texture must be provided.')

        self._prepare_output_texture(next(iter(textures_map.values())).size)

        self.fbo.use()
        self.context.clear(0.0, 0.0, 0.0, 1.0) # 0.0 before

        for name, tex in textures_map.items():
            self.textures.update(name, tex)

        # Set uniforms for this specific moment
        for key, value in kwargs.items():
            self.uniforms.set(key, value)

        self.quad.render()

        return self._output_tex

    # TODO: Overwrite this method
    def process(
        self,
        input: Union[moderngl.Texture, np.ndarray],
        **kwargs
    ) -> moderngl.Texture:
        """
        *This method must be overwritten*

        Apply the shader to the 'input', that
        must be a frame or a texture, and return
        the new resulting texture.

        You can provide any additional parameter
        in the **kwargs, but be careful because
        this could overwrite other uniforms that
        were previously set.

        We use and return textures to maintain
        the process in GPU and optimize it.
        """
        ParameterValidator.validate_mandatory_instance_of('input', input, [moderngl.Texture, np.ndarray])

        textures_map = {
            'tex': input
        }

        return self._process_common(textures_map, **kwargs)
    
class WavingNode(_OpenglNodeBase):
    """
    Just an example, without the shaders code
    actually, to indicate that we can use
    custom parameters to make it work.
    """

    @property
    def vertex_shader(
        self
    ) -> str:
        return (
            '''
            #version 330
            in vec2 in_vert;
            in vec2 in_texcoord;
            out vec2 v_uv;
            void main() {
                v_uv = in_texcoord;
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
            '''
        )

    @property
    def fragment_shader(
        self
    ) -> str:
        return (
            '''
            #version 330
            uniform sampler2D tex;
            uniform float time;
            uniform float amplitude;
            uniform float frequency;
            uniform float speed;
            in vec2 v_uv;
            out vec4 f_color;
            void main() {
                float wave = sin(v_uv.x * frequency + time * speed) * amplitude;
                vec2 uv = vec2(v_uv.x, v_uv.y + wave);
                f_color = texture(tex, uv);
            }
            '''
        )

    def __init__(
        self,
        opengl_context: moderngl.Context,
        size: tuple[int, int],
        amplitude: float = 0.05,
        frequency: float = 10.0,
        speed: float = 2.0
    ):
        super().__init__(
            opengl_context = opengl_context,
            size = size,
            amplitude = amplitude,
            frequency = frequency,
            speed = speed
        )

    def process(
        self,
        input: Union[moderngl.Texture, 'np.ndarray'],
        t: float = 0.0,
    ) -> moderngl.Texture:
        """
        Apply the shader to the 'input', that
        must be a frame or a texture, and return
        the new resulting texture.

        We use and return textures to maintain
        the process in GPU and optimize it.
        """
        return super().process(
            input = input,
            time = t
        )