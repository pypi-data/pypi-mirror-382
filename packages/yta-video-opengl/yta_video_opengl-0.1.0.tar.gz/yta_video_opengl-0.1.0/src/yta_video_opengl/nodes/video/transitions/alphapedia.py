from yta_video_opengl.nodes.video.transitions import _TransitionNode
from yta_validation.parameter import ParameterValidator
from typing import Union

import numpy as np
import moderngl


"""
TODO: This is working with our AlphaPediaYT videos
but it is actually using a video as a mask and it
whould be refactored to work more specifically with
colors or alphas...
"""
# TODO: Maybe rename because this is very specific
class AlphaPediaMaskTransitionNode(_TransitionNode):
    """
    A transition made by using a custom mask to
    join the 2 videos. This mask is specifically
    obtained from the AlphaPediaYT channel in which
    we upload specific masking videos.

    Both videos will be placed occupying the whole
    scene, just overlapping by using the transition
    video mask, but not moving the frame through 
    the screen like other classes do (like the
    FallingBars).
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
        self.textures.add('maskTex', 2)
    
    def process(
        self,
        input_a: Union[moderngl.Texture, 'np.ndarray'],
        input_b: Union[moderngl.Texture, 'np.ndarray'],
        input_mask: Union[moderngl.Texture, 'np.ndarray'],
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
        ParameterValidator.validate_mandatory_instance_of('input_mask', input_mask, [moderngl.Texture, np.ndarray])
        ParameterValidator.validate_mandatory_positive_float('progress', progress, do_include_zero = True)

        textures_map = {
            'texA': input_a,
            'texB': input_b,
            'maskTex': input_mask
        }

        return self._process_common(textures_map, **kwargs)