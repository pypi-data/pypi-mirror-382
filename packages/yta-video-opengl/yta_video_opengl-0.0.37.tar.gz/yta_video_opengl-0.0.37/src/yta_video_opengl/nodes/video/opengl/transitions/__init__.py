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
    
class CircleOpeningTransitionNode(_TransitionNode):
    """
    OpenGL transition in which the frames are mixed
    by generating a circle that grows from the 
    middle to end fitting the whole screen.
    """

    @property
    def vertex_shader(
        self
    ) -> str:
        return (
            """
            #version 330
            in vec2 in_vert;
            in vec2 in_texcoord;
            out vec2 frag_uv;
            void main() {
                frag_uv = in_texcoord;
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
            """
        )
    
    @property
    def fragment_shader(
        self
    ) -> str:
        return (
            """
            #version 330

            uniform sampler2D texA;
            uniform sampler2D texB;
            uniform float progress;  // 0.0 → solo A, 1.0 → solo B
            uniform vec2 resolution; // (width, height)

            in vec2 frag_uv;
            out vec4 frag_color;

            void main() {
                // Coordenadas en píxeles
                vec2 pos = frag_uv * resolution;
                vec2 center = resolution * 0.5;

                // Distancia desde el centro
                float dist = distance(pos, center);

                // Radio actual del círculo
                float maxRadius = length(center);
                float radius = progress * maxRadius;

                // Muestras de las texturas
                vec4 colorA = texture(texA, frag_uv);
                vec4 colorB = texture(texB, frag_uv);

                // With smooth circle
                // TODO: Make this customizable
                float edge = 0.02; // Border smoothness
                float mask = 1.0 - smoothstep(radius - edge * maxRadius, radius + edge * maxRadius, dist);
                frag_color = mix(colorA, colorB, mask);
            }
            """
        )
    
    # TODO: Add 'border_smoothness' attribute
    
class CircleClosingTransitionNode(_TransitionNode):
    """
    OpenGL transition in which the frames are mixed
    by generating a circle that is reduced from its
    whole size to 0.
    """

    @property
    def vertex_shader(
        self
    ) -> str:
        return (
            """
            #version 330
            in vec2 in_vert;
            in vec2 in_texcoord;
            out vec2 frag_uv;
            void main() {
                frag_uv = in_texcoord;
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
            """
        )
    
    @property
    def fragment_shader(
        self
    ) -> str:
        return (
            """
            #version 330

            uniform sampler2D texA;
            uniform sampler2D texB;
            uniform float progress;  // 0.0 → solo A, 1.0 → solo B
            uniform vec2 resolution; // (width, height)

            in vec2 frag_uv;
            out vec4 frag_color;

            void main() {
                // Coordenadas en píxeles
                vec2 pos = frag_uv * resolution;
                vec2 center = resolution * 0.5;

                // Distancia desde el centro
                float dist = distance(pos, center);

                // Radio actual del círculo
                float maxRadius = length(center);
                float radius = (1.0 - progress) * maxRadius;

                // Muestras de las texturas
                vec4 colorA = texture(texA, frag_uv);
                vec4 colorB = texture(texB, frag_uv);

                // With smooth circle
                // TODO: Make this customizable
                float edge = 0.02; // Border smoothness
                float mask = smoothstep(radius - edge * maxRadius, radius + edge * maxRadius, dist);
                frag_color = mix(colorA, colorB, mask);
            }
            """
        )
    
    # TODO: Add 'border_smoothness' attribute

# TODO: Maybe rename because this is very specific
class AlphaPediaMaskTransitionNode(_TransitionNode):
    """
    A transition made by using a custom mask to
    join the 2 videos. This mask is specifically
    obtained from the AlphaPediaYT channel in which
    we upload specific masking videos.
    """

    @property
    def vertex_shader(
        self
    ) -> str:
        return (
            """
            #version 330
            in vec2 in_vert;
            in vec2 in_texcoord;
            out vec2 frag_uv;
            void main() {
                frag_uv = in_texcoord;
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
            """
        )
    
    # TODO: I think I don't need a 'progress' but just
    # mix both frames as much as the alpha (or white
    # presence) tells
    @property
    def fragment_shader(
        self
    ) -> str:
        return (
            """
            #version 330

            uniform sampler2D texA;
            uniform sampler2D texB;
            uniform sampler2D maskTex;

            uniform float progress;  // 0.0 → full A, 1.0 → full B
            uniform bool useAlphaChannel;   // True to use the alpha channel
            //uniform float contrast;  // Optional contrast to magnify the result

            in vec2 frag_uv;
            out vec4 frag_color;

            void main() {
                vec4 colorA = texture(texA, frag_uv);
                vec4 colorB = texture(texB, frag_uv);
                vec4 maskColor = texture(maskTex, frag_uv);

                // Mask alpha or red?
                float maskValue = useAlphaChannel ? maskColor.a : maskColor.r;

                // Optional contrast
                //maskValue = clamp((maskValue - 0.5) * contrast + 0.5, 0.0, 1.0);
                maskValue = clamp((maskValue - 0.5) + 0.5, 0.0, 1.0);

                float t = smoothstep(0.0, 1.0, maskValue + progress - 0.5);

                frag_color = mix(colorA, colorB, t);
            }
            """
        )
    
    @force_inputs_as_textures
    def process(
        self,
        input_a: Union[moderngl.Texture, 'np.ndarray'],
        input_b: Union[moderngl.Texture, 'np.ndarray'],
        input_mask: Union[moderngl.Texture, 'np.ndarray'],
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
        # Bind the mask texture
        input_mask.use(location = 2)
        self.program['maskTex'] = 2

        # Set 'progress' to handle the transition progress
        if 'progress' in self.program:
            self.program['progress'].value = progress

        # Set any existing uniform dynamically
        for key, value in kwargs.items():
            self.uniforms.set(key, value)

        self.quad.render()

        return self.output_tex