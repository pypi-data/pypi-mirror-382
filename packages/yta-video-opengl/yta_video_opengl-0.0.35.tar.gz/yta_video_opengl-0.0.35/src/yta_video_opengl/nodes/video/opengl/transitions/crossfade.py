from yta_video_opengl.nodes.video.opengl.transitions import _TransitionNode

import moderngl


class CrossfadeTransitionNode(_TransitionNode):
    """
    OpenGL transition in which the frames are mixed
    with a simple crossfade.
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
            uniform float progress; // 0 = solo A, 1 = solo B
            in vec2 frag_uv;
            out vec4 frag_color;
            void main() {
                vec4 cA = texture(texA, frag_uv);
                vec4 cB = texture(texB, frag_uv);
                frag_color = mix(cA, cB, progress);
            }
            """
        )
    
class DistortedCrossfadeTransitionNode(_TransitionNode):
    """
    OpenGL transition in which the frames are mixed
    with a distorted crossfade.
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
            uniform float progress;   // 0.0 -> A, 1.0 -> B
            uniform float intensity;  // Distortion control
            in vec2 frag_uv;
            out vec4 frag_color;

            const int passes = 6;

            void main() {
                vec4 c1 = vec4(0.0);
                vec4 c2 = vec4(0.0);

                float disp = intensity * (0.5 - distance(0.5, progress));
                for (int xi=0; xi<passes; xi++) {
                    float x = float(xi) / float(passes) - 0.5;
                    for (int yi=0; yi<passes; yi++) {
                        float y = float(yi) / float(passes) - 0.5;
                        vec2 v = vec2(x, y);
                        float d = disp;
                        c1 += texture(texA, frag_uv + d * v);
                        c2 += texture(texB, frag_uv + d * v);
                    }
                }
                c1 /= float(passes * passes);
                c2 /= float(passes * passes);
                frag_color = mix(c1, c2, progress);
            }
            """
        )
    
    def __init__(
        self,
        context: moderngl.Context,
        size: tuple[int, int],
        intensity: float = 0.1
    ):
        super().__init__(
            context = context,
            size = size,
            intensity = intensity
        )