"""
Experimental module. The effects here
have not been tested completely or the
result is not as good as it should be
to be considered a definitive effect.
"""
from yta_video_opengl.nodes.video.opengl import OpenglNodeBase
from typing import Union

import numpy as np
import moderngl
import math


class BreathingFrame(OpenglNodeBase):
    """
    The frame but as if it was breathing.
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
            out vec2 v_text;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                v_text = in_texcoord;
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
            in vec2 v_text;
            out vec4 f_color;
            // Use uniforms to be customizable

            void main() {
                // Dynamic zoom scaled with t
                float scale = 1.0 + 0.05 * sin(time * 2.0);  // 5% de zoom
                vec2 center = vec2(0.5, 0.5);

                // Recalculate coords according to center
                vec2 uv = (v_text - center) / scale + center;

                // Clamp to avoid artifacts
                uv = clamp(uv, 0.0, 1.0);

                f_color = texture(tex, uv);
            }
            '''
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
        self.uniforms.set('time', t)

        return super().process(input)
    
class HandheldFrame(OpenglNodeBase):
    """
    The frame but as if it was being recorder by
    someone holding a camera, that is not 100%
    stable.
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
            out vec2 v_text;

            uniform mat3 transform;

            void main() {
                vec3 pos = vec3(in_vert, 1.0);
                pos = transform * pos;
                gl_Position = vec4(pos.xy, 0.0, 1.0);
                v_text = in_texcoord;
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
            in vec2 v_text;
            out vec4 f_color;

            void main() {
                f_color = texture(tex, v_text);
            }
            '''
        )
    
    def _handheld_matrix(
        self,
        t
    ):
        # Rotación más notoria
        angle = self._smooth_noise(t, freq=0.8, scale=0.05)  # antes 0.02

        # Traslaciones más grandes
        tx = self._smooth_noise(t, freq=1.1, scale=0.04)     # antes 0.015
        ty = self._smooth_noise(t, freq=1.4, scale=0.04)

        # Zoom más agresivo
        zoom = 1.0 + self._smooth_noise(t, freq=0.5, scale=0.06)  # antes 0.02

        cos_a, sin_a = math.cos(angle), math.sin(angle)

        return np.array([
            [ cos_a * zoom, -sin_a * zoom, tx],
            [ sin_a * zoom,  cos_a * zoom, ty],
            [ 0.0,           0.0,          1.0]
        ], dtype="f4")

    def _smooth_noise(
        self,
        t,
        freq = 1.5,
        scale = 1.0
    ):
        """
        Small noise by using sin and cos mixed.
        """
        return (
            math.sin(t * freq) +
            0.5 * math.cos(t * freq * 0.5 + 1.7) +
            0.25 * math.sin(t * freq * 0.25 + 2.5)
        ) * scale
    
    def process(
        self,
        input: Union[moderngl.Texture, np.ndarray],
        t: float = 0.0,
    ) -> moderngl.Texture:
        """
        Apply the shader to the 'input', that
        must be a frame or a texture, and return
        the new resulting texture.

        We use and return textures to maintain
        the process in GPU and optimize it.
        """
        self.uniforms.set_mat('transform', self._handheld_matrix(t).tobytes())

        return super().process(input)
    
class OrbitingFrame(OpenglNodeBase):
    """
    The frame but orbiting around the camera.
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

            uniform mat4 mvp;   // Model-View-Projection matrix

            void main() {
                v_uv = in_texcoord;
                // El quad está en XY, lo pasamos a XYZ con z=0
                vec4 pos = vec4(in_vert, 0.0, 1.0);
                gl_Position = mvp * pos;
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
            in vec2 v_uv;
            out vec4 f_color;

            void main() {
                f_color = texture(tex, v_uv);
            }
            '''
        )
    
    def _perspective(
        self,
        fov_y_rad,
        aspect,
        near,
        far
    ):
        f = 1.0 / np.tan(fov_y_rad / 2.0)
        m = np.zeros((4,4), dtype='f4')
        m[0,0] = f / aspect
        m[1,1] = f
        m[2,2] = (far + near) / (near - far)
        m[2,3] = (2 * far * near) / (near - far)
        m[3,2] = -1.0

        return m
    
    def _look_at(
        self,
        eye,
        target,
        up = (0, 1, 0)
    ):
        eye = np.array(eye, dtype='f4')
        target = np.array(target, dtype='f4')
        up = np.array(up, dtype='f4')

        f = target - eye
        f = f / np.linalg.norm(f)
        s = np.cross(f, up)
        s = s / np.linalg.norm(s)
        u = np.cross(s, f)

        m = np.eye(4, dtype='f4')
        m[0,0:3] = s
        m[1,0:3] = u
        m[2,0:3] = -f
        m[0,3] = -np.dot(s, eye)
        m[1,3] = -np.dot(u, eye)
        m[2,3] =  np.dot(f, eye)

        return m

    def _translate(
        self,
        x,
        y,
        z
    ):
        m = np.eye(4, dtype='f4')
        m[0,3] = x
        m[1,3] = y
        m[2,3] = z

        return m

    def _rotate_y(
        self,
        angle
    ):
        c, s = np.cos(angle), np.sin(angle)
        m = np.eye(4, dtype='f4')
        m[0,0], m[0,2] =  c,  s
        m[2,0], m[2,2] = -s,  c

        return m
    
    def _scale_uniform(
        self,
        k
    ):
        m = np.eye(4, dtype='f4')
        m[0,0] = m[1,1] = m[2,2] = k

        return m
    
    def _carousel_mvp(
        self,
        t,
        *,
        aspect,
        fov_deg = 60.0,
        radius = 4.0,
        center_z = -6.0,
        speed = 1.0,
        face_center_strength = 1.0,
        extra_scale = 1.0
    ):
        """
        t: tiempo en segundos
        aspect: width/height del framebuffer
        radius: radio en XZ
        center_z: desplaza el carrusel entero hacia -Z para que esté frente a cámara
        speed: velocidad angular
        face_center_strength: 1.0 = panel mira al centro; 0.0 = no gira con la órbita
        """

        # Proyección y vista (cámara en el origen mirando hacia -Z)
        proj = self._perspective(np.radians(fov_deg), aspect, 0.1, 100.0)
        view = np.eye(4, dtype='f4')  # o look_at((0,0,0), (0,0,-1))

        # Ángulo de órbita (elige el offset para que "entre" por la izquierda)
        theta = speed * t - np.pi * 0.5

        # Órbita en XZ con el centro desplazado a center_z
        # x = radius * np.cos(theta)
        # z = radius * np.sin(theta) + center_z
        x = radius * np.cos(theta)
        z = (radius * 0.2) * np.sin(theta) + center_z

        # Yaw para que el panel apunte al centro (0,0,center_z)
        # El vector desde panel -> centro es (-x, 0, center_z - z)
        yaw_to_center = np.arctan2(-x, (center_z - z))  # atan2(X, Z)
        yaw = face_center_strength * yaw_to_center

        model = self._translate(x, 0.0, z) @ self._rotate_y(yaw) @ self._scale_uniform(extra_scale)

        # ¡IMPORTANTE! OpenGL espera column-major: transponemos al escribir
        mvp = proj @ view @ model
        
        return mvp
    
    def process(
        self,
        input: Union[moderngl.Texture, np.ndarray],
        t: float = 0.0,
    ) -> moderngl.Texture:
        """
        Apply the shader to the 'input', that
        must be a frame or a texture, and return
        the new resulting texture.

        We use and return textures to maintain
        the process in GPU and optimize it.
        """
        aspect = self.size[0] / self.size[1]
        mvp = self._carousel_mvp(t, aspect=aspect, radius=4.0, center_z=-4.0, speed=1.2, face_center_strength=1.0, extra_scale = 1.0)

        self.uniforms.set_mat('mvp', mvp.T.tobytes())

        return super().process(input)
    
class RotatingInCenterFrame(OpenglNodeBase):
    """
    The frame but orbiting around the camera.
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

            uniform float time;
            uniform float speed;

            void main() {
                v_uv = in_texcoord;

                // Rotación alrededor del eje Y
                float angle = time * speed;              // puedes usar time directamente, o time * speed
                float cosA = cos(angle);
                float sinA = sin(angle);

                // Convertimos el quad a 3D (x, y, z)
                vec3 pos = vec3(in_vert.xy, 0.0);

                // Rotación Y
                mat3 rotY = mat3(
                    cosA, 0.0, sinA,
                    0.0 , 1.0, 0.0,
                -sinA, 0.0, cosA
                );

                pos = rotY * pos;

                gl_Position = vec4(pos, 1.0);
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

            in vec2 v_uv;
            out vec4 f_color;

            uniform sampler2D tex;

            void main() {
                f_color = texture(tex, v_uv);
            }
            '''
        )
    
    def __init__(
        self,
        size,
        first_frame,
        context = None,
        speed: float = 30
    ):
        super().__init__(size, first_frame, context)

        self.uniforms.set('speed', speed)

    def process(
        self,
        input: Union[moderngl.Texture, np.ndarray],
        t: float = 0.0,
    ) -> moderngl.Texture:
        """
        Apply the shader to the 'input', that
        must be a frame or a texture, and return
        the new resulting texture.

        We use and return textures to maintain
        the process in GPU and optimize it.
        """
        self.uniforms.set('time', t)

        return super().process(input)
    
class StrangeTvFrame(OpenglNodeBase):
    """
    Nice effect like a tv screen or something...
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

            // ---- Parámetros principales (ajústalos en runtime) ----
            uniform float aberr_strength;  // 0..3   (fuerza del RGB split radial)
            uniform float barrel_k;        // -0.5..0.5  (distorsión de lente; positivo = barrel)
            uniform float blur_radius;     // 0..0.02 (radio de motion blur en UV)
            uniform float blur_angle;      // en radianes (dirección del arrastre)
            uniform int   blur_samples;    // 4..24  (taps del blur)
            uniform float vignette_strength; // 0..2
            uniform float grain_amount;    // 0..0.1
            uniform float flicker_amount;  // 0..0.2
            uniform float scanline_amount; // 0..0.2

            in vec2 v_uv;
            out vec4 f_color;

            // --- helpers ---
            float rand(vec2 co){
                return fract(sin(dot(co, vec2(12.9898,78.233))) * 43758.5453);
            }

            // Barrel distortion (simple, k>0 curva hacia fuera)
            vec2 barrel(vec2 uv, float k){
                // map to [-1,1]
                vec2 p = uv * 2.0 - 1.0;
                float r2 = dot(p, p);
                p *= (1.0 + k * r2);
                // back to [0,1]
                return p * 0.5 + 0.5;
            }

            // Aberración cromática radial
            vec3 sample_chromatic(sampler2D t, vec2 uv, vec2 center, float strength){
                // Offset radial según distancia al centro
                vec2 d = uv - center;
                float r = length(d);
                vec2 dir = (r > 1e-5) ? d / r : vec2(0.0);
                // Cada canal se desplaza un poco distinto
                float s = strength * r * 0.005; // escala fina
                float sr = s * 1.0;
                float sg = s * 0.5;
                float sb = s * -0.5; // azul hacia dentro para contraste

                float rC = texture(t, uv + dir * sr).r;
                float gC = texture(t, uv + dir * sg).g;
                float bC = texture(t, uv + dir * sb).b;
                return vec3(rC, gC, bC);
            }

            void main(){
                vec2 uv = v_uv;
                vec2 center = vec2(0.5, 0.5);

                // Lente (barrel/pincushion)
                uv = barrel(uv, barrel_k);

                // Early out si nos salimos mucho (fade de bordes)
                vec2 uv_clamped = clamp(uv, 0.0, 1.0);
                float edge = smoothstep(0.0, 0.02, 1.0 - max(max(-uv.x, uv.x-1.0), max(-uv.y, uv.y-1.0)));

                // Dirección del motion blur
                vec2 dir = vec2(cos(blur_angle), sin(blur_angle));
                // Pequeña variación temporal para que “respire”
                float jitter = (sin(time * 13.0) * 0.5 + 0.5) * 0.4 + 0.6;

                // Acumulación de blur con pesos
                vec3 acc = vec3(0.0);
                float wsum = 0.0;

                int N = max(1, blur_samples);
                for(int i = 0; i < 64; ++i){         // hard cap de seguridad
                    if(i >= N) break;
                    // t de -1..1 distribuye muestras a ambos lados
                    float fi = float(i);
                    float t = (fi / float(N - 1)) * 2.0 - 1.0;

                    // curva de pesos (gauss approx)
                    float w = exp(-t*t * 2.5);
                    // offset base
                    vec2 ofs = dir * t * blur_radius * jitter;

                    // micro-jitter por muestra para romper banding
                    ofs += vec2(rand(uv + fi)*0.0005, rand(uv + fi + 3.14)*0.0005) * blur_radius;

                    // muestreo con aberración cromática
                    vec3 c = sample_chromatic(tex, uv + ofs, center, aberr_strength);

                    acc += c * w;
                    wsum += w;
                }
                vec3 col = acc / max(wsum, 1e-6);

                // Scanlines + flicker
                float scan = 1.0 - scanline_amount * (0.5 + 0.5 * sin((uv.y + time*1.7)*3.14159*480.0));
                float flick = 1.0 + flicker_amount * (sin(time*60.0 + uv.x*10.0) * 0.5 + 0.5);
                col *= scan * flick;

                // Vignette (radial)
                float r = distance(uv, center);
                float vig = 1.0 - smoothstep(0.7, 1.0, r * (1.0 + 0.5*vignette_strength));
                col *= mix(1.0, vig, vignette_strength);

                // Grano
                float g = (rand(uv * (time*37.0 + 1.0)) - 0.5) * 2.0 * grain_amount;
                col += g;

                // Fade de bordes por clamp/warp
                col *= edge;

                f_color = vec4(col, 1.0);
            }
            '''
        )
    
    def __init__(
        self,
        size,
        first_frame,
        context = None,
        aberr_strength = 1.5,
        barrel_k = 0.08,
        blur_radius = 0.006,
        blur_angle = 0.0, # (0 = horizontal, 1.57 ≈ vertical)
        blur_samples = 12,
        vignette_strength = 0.8,
        grain_amount = 0.02,
        flicker_amount = 0.05,
        scanline_amount = 0.05
    ):
        super().__init__(size, first_frame, context)

        self.uniforms.set('aberr_strength', aberr_strength)
        self.uniforms.set('barrel_k', barrel_k)
        self.uniforms.set('blur_radius', blur_radius)
        self.uniforms.set('blur_angle', blur_angle)
        self.uniforms.set('blur_samples', blur_samples)
        self.uniforms.set('vignette_strength', vignette_strength)
        self.uniforms.set('grain_amount', grain_amount)
        self.uniforms.set('flicker_amount', flicker_amount)
        self.uniforms.set('scanline_amount', scanline_amount)

    def process(
        self,
        input: Union[moderngl.Texture, np.ndarray],
        t: float = 0.0,
    ) -> moderngl.Texture:
        """
        Apply the shader to the 'input', that
        must be a frame or a texture, and return
        the new resulting texture.

        We use and return textures to maintain
        the process in GPU and optimize it.
        """
        self.uniforms.set('time', t)

        return super().process(input)
    
class GlitchRgbFrame(OpenglNodeBase):
    """
    Nice effect like a tv screen or something...
    """

    @property
    def vertex_shader(
        self
    ) -> str:
        return (
            '''
            #version 330

            // ----------- Vertex Shader -----------
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

            // ----------- Fragment Shader -----------
            uniform sampler2D tex;
            uniform float time;

            // Intensidades del efecto
            uniform float amp;      // amplitud de distorsión
            uniform float freq;     // frecuencia de la onda
            uniform float glitchAmp; // fuerza del glitch
            uniform float glitchSpeed;

            in vec2 v_uv;
            out vec4 f_color;

            void main() {
                // Distorsión sinusoidal en Y
                float wave = sin(v_uv.x * freq + time * 2.0) * amp;

                // Pequeño desplazamiento aleatorio (shake)
                float shakeX = (fract(sin(time * 12.9898) * 43758.5453) - 0.5) * 0.01;
                float shakeY = (fract(sin(time * 78.233) * 12345.6789) - 0.5) * 0.01;

                // Coordenadas base con distorsión
                vec2 uv = vec2(v_uv.x + shakeX, v_uv.y + wave + shakeY);

                // Glitch con separación RGB
                float glitch = sin(time * glitchSpeed) * glitchAmp;
                vec2 uv_r = uv + vec2(glitch, 0.0);
                vec2 uv_g = uv + vec2(-glitch * 0.5, glitch * 0.5);
                vec2 uv_b = uv + vec2(0.0, -glitch);

                // Muestreo canales desplazados
                float r = texture(tex, uv_r).r;
                float g = texture(tex, uv_g).g;
                float b = texture(tex, uv_b).b;

                f_color = vec4(r, g, b, 1.0);
            }
            '''
        )
    
    def __init__(
        self,
        size,
        first_frame,
        context = None,
        amp = 0.02,
        freq = 25.0,
        glitchAmp = 0.02,
        glitchSpeed = 30.0
    ):
        super().__init__(size, first_frame, context)

        self.uniforms.set('amp', amp)
        self.uniforms.set('freq', freq)
        self.uniforms.set('glitchAmp', glitchAmp)
        self.uniforms.set('glitchSpeed', glitchSpeed)

    def process(
        self,
        input: Union[moderngl.Texture, np.ndarray],
        t: float = 0.0,
    ) -> moderngl.Texture:
        """
        Apply the shader to the 'input', that
        must be a frame or a texture, and return
        the new resulting texture.

        We use and return textures to maintain
        the process in GPU and optimize it.
        """
        self.uniforms.set('time', t)

        return super().process(input)