"""
TODO: Note for the developer:

Check the '.gsls' files and make sure the 
variables names fit the expected ones:
- `in_pos` must be renamed to `in_vert`
- `in_uv` must be renamed to `in_texcoord`
- Textures should be called `tex`, `texA`,
`texB`, `maskTex`, etc. according to the
code we are handling.

We are using 2 specific methods to build
our own classes:
- `_prepare_input_textures` to initialize
the texture variables.
- `process` to receive the inputs, handle
them and link to an specific texture.
Create a new class with their shaders and
this custom method to be able to handle 
them.
"""
from yta_video_opengl.nodes.video import _OpenglNodeBase
from yta_validation.parameter import ParameterValidator
from typing import Union
from abc import abstractmethod

import numpy as np
import moderngl


class _TransitionNode(_OpenglNodeBase):
    """
    *For internal use only*

    Base Transition Node to be inherited by
    the transitions we create that handle 2
    different textures.

    These are the variable names of the 
    textures within the '.gsls' code:
    - `texA` - The texture of the first clip
    - `texB` - The texture of the second clip
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

    def _prepare_input_textures(
        self
    ) -> None:
        """
        *For internal use only*

        Set the input texture variables and handlers
        we need to manage this.
        """
        self.textures.add('texA', 0)
        self.textures.add('texB', 1)

    def process(
        self,
        input_a: Union[moderngl.Texture, 'np.ndarray'],
        input_b: Union[moderngl.Texture, 'np.ndarray'],
        progress: float,
        **kwargs
    ) -> moderngl.Texture:
        """
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
        ParameterValidator.validate_mandatory_instance_of('input_a', input_a, [moderngl.Texture, np.ndarray])
        ParameterValidator.validate_mandatory_instance_of('input_b', input_b, [moderngl.Texture, np.ndarray])
        ParameterValidator.validate_mandatory_positive_float('progress', progress, do_include_zero = True)

        textures_map = {
            'texA': input_a,
            'texB': input_b
        }

        kwargs = {
            **kwargs,
            'progress': progress
        }

        return self._process_common(textures_map, **kwargs)

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
    
class BarsFallingTransitionNode(_TransitionNode):
    """
    OpenGL transition based on a set of bars that
    fall with the first video to let the second
    one be seen.

    Extracted from here:
    - https://gl-transitions.com/editor/DoomScreenTransition
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
            uniform float progress; // 0.0 → start, 1.0 → end

            uniform int bars;           
            uniform float amplitude;    // Speed
            uniform float noise;        // Extra noise [0.0, 1.0]
            uniform float frequency;    // Wave frequency
            uniform float dripScale;    // Falling from center

            in vec2 frag_uv;
            out vec4 frag_color;

            // pseudo-random from integer
            float rand(int num) {
                return fract(mod(float(num) * 67123.313, 12.0) * sin(float(num) * 10.3) * cos(float(num)));
            }

            // Wave for vertical distortion
            float wave(int num) {
                float fn = float(num) * frequency * 0.1 * float(bars);
                return cos(fn * 0.5) * cos(fn * 0.13) * sin((fn + 10.0) * 0.3) / 2.0 + 0.5;
            }

            // Vertical curve to borders
            float drip(int num) {
                return sin(float(num) / float(bars - 1) * 3.141592) * dripScale;
            }

            // Displacement for a bar
            float pos(int num) {
                float w = wave(num);
                float r = rand(num);
                float base = (noise == 0.0) ? w : mix(w, r, noise);
                return base + ((dripScale == 0.0) ? 0.0 : drip(num));
            }

            void main() {
                int bar = int(frag_uv.x * float(bars));

                float scale = 1.0 + pos(bar) * amplitude;
                float phase = progress * scale;
                float posY = frag_uv.y;

                vec2 p;
                vec4 color;

                if (phase + posY < 1.0) {
                    // Frame A visible
                    p = vec2(frag_uv.x, frag_uv.y + mix(0.0, 1.0, phase));
                    color = texture(texA, p);
                } else {
                    // Frame B visible
                    color = texture(texB, frag_uv);
                }

                frag_color = color;
            }
            """
        )