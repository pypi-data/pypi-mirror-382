"""
Module to include the transitions that are made
with the OpenGL engine.
"""
from yta_video_opengl.utils import frame_to_texture, texture_to_frame
from typing import Union

import numpy as np
import moderngl


# class WipeOpenGLTransition(GLTransition):
#     """
#     A wipe transition but made with OpenGL.
#     """

#     # TODO: Refactor this to inherit from the classes
#     # we have in the 'yta_video_opengl'
    
#     @property
#     def vertex_shader(
#         self
#     ) -> str:
#         return (
#             '''
#             #version 330
#             in vec2 in_vert;
#             in vec2 in_texcoord;
#             out vec2 v_uv;
#             void main() {
#                 v_uv = in_texcoord;
#                 gl_Position = vec4(in_vert, 0.0, 1.0);
#             }
#             '''
#         )
    
#     # --- Fragment shader con proyección 3D simulada
#     @property
#     def fragment_shader(self) -> str:
#         dir_expr = {
#             "horizontal": "uv.x",
#             "vertical": "uv.y",
#             "diagonal": "(uv.x + uv.y) * 0.5"
#         }[self.direction]

#         if self.reverse:
#             dir_expr = f"(1.0 - {dir_expr})"

#         # Si es horizontal, rotamos en eje Y; si vertical, en X
#         axis = {
#             "horizontal": "y",
#             "vertical": "x",
#             "diagonal": "xy"
#         }[self.direction]

#         return (
#             '''
#             #version 330

#             uniform sampler2D tex_a;   // Frame A (saliente)
#             uniform sampler2D tex_b;   // Frame B (entrante)
#             uniform float u_progress;  // Progreso de 0.0 a 1.0

#             in vec2 v_uv;
#             out vec4 f_color;

#             void main() {
#                 // Coordenada desplazada (wipe horizontal)
#                 float wipe = step(v_uv.x, u_progress);

#                 // Aplica rotación leve en Z para efecto 3D
#                 float angle = mix(-0.3, 0.3, u_progress);
#                 mat2 rot = mat2(cos(angle), -sin(angle), sin(angle), cos(angle));
#                 vec2 uv_rot = (v_uv - 0.5) * rot + 0.5;

#                 // Muestras de ambas texturas
#                 vec4 color_a = texture(tex_a, uv_rot);
#                 vec4 color_b = texture(tex_b, uv_rot);

#                 // Mezcla según el progreso
#                 f_color = mix(color_a, color_b, wipe);
#             }
#             '''
#         )
    
#     def __init__(
#         self,
#         ctx: moderngl.Context,
#         direction: str = "horizontal",  # horizontal | vertical | diagonal
#         reverse: bool = False,
#         softness: float = 0.05,
#         depth: float = 0.3,
#     ):
#         super().__init__(ctx, TransitionParams(0.0, softness, depth))
#         self.direction = direction
#         self.reverse = reverse


    # # Simple version below:
    # @property
    # def fragment_shader(
    #     self
    # ) -> str:
    #     # Construcción dinámica según dirección
    #     dir_expr = {
    #         "horizontal": "uv.x",
    #         "vertical": "uv.y",
    #         "diagonal": "(uv.x + uv.y) * 0.5"
    #     }[self.direction]

    #     # Si es invertido → (1.0 - ...)
    #     if self.reverse:
    #         dir_expr = f"(1.0 - {dir_expr})"

    #     return (
    #         f'''
    #         #version 330
    #         uniform sampler2D tex_a;
    #         uniform sampler2D tex_b;
    #         uniform float time;      // progreso de la transición (0.0 → 1.0)
    #         uniform float softness;  // borde difuminado opcional

    #         in vec2 v_uv;
    #         out vec4 f_color;

    #         void main() {{
    #             vec2 uv = v_uv;
    #             float edge = {dir_expr};

    #             // Transición: comparar edge con 'time'
    #             float m = edge - time;

    #             // Borde suave si softness > 0
    #             float blend = smoothstep(-softness, softness, -m);

    #             vec4 colorA = texture(tex_a, uv);
    #             vec4 colorB = texture(tex_b, uv);

    #             f_color = mix(colorA, colorB, blend);
    #         }}
    #         '''
    #     )

# TODO: This code on top has to be removed
# but some parts are interesting, like the 
# smooth border made with 'softness' and
# 'smoothstep'

from yta_editor.track.media.video import VideoOnTrack
from yta_editor.media.video import _VideoMedia
from yta_video_opengl.nodes.video.opengl.transitions.crossfade import CrossfadeTransitionNode, DistortedCrossfadeTransitionNode
from yta_video_opengl.nodes.video.opengl.transitions.slide import SlideTransitionNode
from yta_video_opengl.nodes.video.opengl.transitions import CircleOpeningTransitionNode, CircleClosingTransitionNode, AlphaPediaMaskTransitionNode
from yta_video_opengl.utils import frame_to_texture, texture_to_frame
from yta_video_frame_time.t_fraction import get_ts, fps_to_time_base, T
from yta_video_pyav.writer import VideoWriter
from yta_video_pyav.settings import Settings
from yta_validation.parameter import ParameterValidator
from av.video.frame import VideoFrame
from quicktions import Fraction
from typing import Union

import numpy as np


class _OpenglTransitionMedia:
    """
    Class to wrap a transition clip, that is a
    clip in which 2 clips are joined with another
    transition clip.

    TODO: This below is temporary
    The clips will be placed consecutive and the
    transition will be played in between, joining
    both.
    """

    @property
    def _start(
        self
    ) -> Fraction:
        """
        *For internal use only*

        The moment in which the transition clip starts
        being played, that will be in some moment of
        the first clip, and it should be also the 
        moment in which the second clip starts being
        played (with the corresponding transition
        blending).
        """
        # TODO: This value is only valid for the transition
        # applied in the middle with 50%-50% strategy
        return self._clip_a.duration - self.duration
    
    @property
    def _end(
        self
    ) -> Fraction:
        """
        *For internal use only*

        The moment in which the whole clip built with
        the transition in the middle must stop being
        played, so the second clip has finished.
        """
        return self._clip_b.end

    def __init__(
        self,
        # TODO: This '_MediaOnTrack' has to be renamed 
        # because here it is not on a track but the class
        # we need is this one
        # TODO: Maybe it has to be just a Media, not OnTrack
        clip_a: _VideoMedia,
        clip_b: _VideoMedia,
        duration: float,
        # TODO: This has to be passed always from the editor
        opengl_context: 'context' = None
    ):
        ParameterValidator.validate_subclass_of('clip_a', clip_a, _VideoMedia)
        ParameterValidator.validate_subclass_of('clip_b', clip_b, _VideoMedia)

        if (
            clip_a.duration < duration or
            clip_b.duration < duration
        ):
            raise Exception('The duration of one of the clips is smaller than the transition duration requested.')

        # TODO: Apply Union[AlphaBlendTransition, ...]
        self.duration: float = duration
        """
        The duration of the transition.
        """

        # TODO: This should be received always from the
        # editor but by now we are creating it here
        self.context: 'Context' = (
            moderngl.create_context(standalone = True)
            if opengl_context is None else
            opengl_context
        )
        """
        The OpenGL context to work properly with the
        engine, the framebuffers, etc.
        """
        # TODO: Rename different than OnTrack
        self._clip_a: VideoOnTrack = VideoOnTrack(
            media = clip_a,
            start = 0
        )
        """
        The first clip to join in with the transition.
        """
        # TODO: Rename different than OnTrack
        self._clip_b: VideoOnTrack = VideoOnTrack(
            media = clip_b,
            start = self._start
        )
        """
        The second clip to join in with the transition.
        """

        # TODO: The child class must implement the
        # 'self.opengl_node' variable
        # self.opengl_node: 'OpenglNodeBase' = CrossfadeTransitionNode(
        #     context = self.context,
        #     # TODO: Do not hardcode, please
        #     size = (1920, 1080),
        # )
    
    # TODO: We manually handle the time in which
    # we are applying the transition and use the
    # blend factor only there, so this method is
    # unnecessary I think unless we use a curve
    # and not a linear blend factor
    def get_blend_factor_at_t(
        self,
        t: float
    ) -> float:
        """
        Get the weight of the second clip at the
        't' time moment provided as a value in the
        [0.0, 1.0] range.

        The `t` time moment provided must be a 
        time moment in between 0 and the end of
        the whole transition.

        TODO: What (?)
        The `t` is the time moment since the start
        of the transition.
        """
        if t < 0:
            return 0.0
        
        if t > self.duration:
            return 1.0
        
        """
        By now, the transition we are applying is
        as simple as being in the middle of the 2
        clips provided and lasting the 'duration'
        provided, being executed with a linear t.
        """

        # TODO: The ratios are to adjust the internal
        # duration but we are not using them by now
        # Normalización según start/end ratios
        # ratio_range = self.end_ratio - self.start_ratio
        # norm_t = (t / self.duration - self.start_ratio) / ratio_range
        # norm_t = max(0.0, min(1.0, norm_t))

        norm_t = (t / self.duration)
        norm_t = max(0.0, min(1.0, norm_t))

        # The curve is a param to adjust the transition
        # speed that we are not handling by now
        curve = 0.0
        # TODO: By now we have one simple way of
        # handling the 't' value
        norm_t = norm_t ** (1 + curve)

        # # Easing
        # if self.ease == TransitionEase.EASE_IN:
        #     norm_t = norm_t ** (1 + self.curve)
        # elif self.ease == TransitionEase.EASE_OUT:
        #     norm_t = 1 - (1 - norm_t) ** (1 + self.curve)
        # elif self.ease == TransitionEase.EASE_IN_OUT:
        #     # curva suave simétrica
        #     norm_t = 0.5 * (1 - (1 - 2 * norm_t) ** (1 + self.curve)) if norm_t < 0.5 else \
        #              0.5 + 0.5 * (2 * norm_t - 1) ** (1 + self.curve)

        return norm_t
    
    def get_video_frame_at(
        self,
        t: Union[int, float, Fraction],
        do_apply_filters: bool = False
    ) -> VideoFrame:
        """
        The `t` time moment provided must be a global
        time value pointing to a moment in the general
        timeline. That value will be transformed to the
        internal `t` value to get the frame.
        """
        # Test with OpenGL
        frame_a = self._clip_a.get_video_frame_at(t)
        frame_b = self._clip_b.get_video_frame_at(t)

        if (
            frame_a is None and
            frame_b is None
        ):
            print('Both None, wtf')
            #return None

        """
        There is a moment in which we are not in
        the transition section but on the clips
        so we just need to return the clip frames.
        """
        if frame_b is None:
            # Not transition time, just one clip
            out_frame = frame_a
            out_frame.pts = None
            out_frame.time_base = Fraction(1, 60)

            return out_frame
        
        if frame_a is None:
            # Not transition time, just one clip
            out_frame = frame_b
            out_frame.pts = None
            out_frame.time_base = Fraction(1, 60)

            return out_frame
        # Render loop

        t_progress = (t - self._start) / self.duration
        frame_a = frame_a.to_ndarray(format = 'rgb24').astype(np.float32)
        frame_b = frame_b.to_ndarray(format = 'rgb24').astype(np.float32)

        # TODO: Do we need the alpha? Maybe to mix with
        # something else
        return self._process_frame(
            frame_a = frame_a,
            frame_b = frame_b,
            t_progress = t_progress
        )
    
    # @abstractmethod
    # def _process_frame(
    #     self,
    #     # numpy array or texture
    #     frame_a: any,
    #     # numpy array or texture
    #     frame_b: any,
    #     t_progress: float,
    # ):
    #     pass

    # TODO: This method can be overwritten to change
    # its behaviour if the specific transition needs
    # it
    def _process_frame(
        self,
        # numpy array or texture
        frame_a: any,
        # numpy array or texture
        frame_b: any,
        t_progress: float,
    ):
        # TODO: Maybe this can be placed in the general
        # class if it doesn't change
        frame = VideoFrame.from_ndarray(
            array = texture_to_frame(
                texture = self.opengl_node.process(
                    input_a = frame_a,
                    input_b = frame_b,
                    progress = t_progress
                ),
                do_include_alpha = False
            ).astype(np.uint8),
            format = 'rgb24'
        )
        # The 'pts' and that is not important here but...
        frame.pts = None
        frame.time_base = Fraction(1, 60)

        return frame

    def save_as(
        self,
        output_filename: str,
        video_size: tuple[int, int] = None,
        video_fps: float = None,
        video_codec: str = None,
        video_pixel_format: str = None,
        audio_codec: str = None,
        audio_sample_rate: int = None,
        audio_layout: str = None,
        audio_format: str = None,
        do_apply_video_filters: bool = True,
        do_apply_audio_filters: bool = True
    ) -> str:
        """
        Save the file as 'output_filename'.

        This method is useful if you want to apply
        some filter and then save the video with
        those filters applied into a new one, maybe
        with a new pixel format and/or code. You can
        prepare alpha transitions, etc.
        """
        video_size = (
            getattr(self, 'size', Settings.DEFAULT_VIDEO_SIZE.value)
            if video_size is None else
            video_size
        )

        video_fps = (
            getattr(self, 'fps', Settings.DEFAULT_VIDEO_FPS.value)
            if video_fps is None else
            video_fps
        )

        video_codec = (
            getattr(self, 'codec_name', Settings.DEFAULT_VIDEO_CODEC.value)
            if video_codec is None else
            video_codec
        )

        video_pixel_format = (
            getattr(self, 'pixel_format', Settings.DEFAULT_PIXEL_FORMAT.value)
            if video_pixel_format is None else
            video_pixel_format
        )

        audio_codec = (
            getattr(self, 'audio_codec_name', Settings.DEFAULT_AUDIO_CODEC.value)
            if audio_codec is None else
            audio_codec
        )

        audio_sample_rate = (
            getattr(self, 'audio_fps', Settings.DEFAULT_AUDIO_FPS.value)
            if audio_sample_rate is None else
            audio_sample_rate
        )

        audio_layout = (
            getattr(self, 'audio_layout', Settings.DEFAULT_AUDIO_LAYOUT.value)
            if audio_layout is None else
            audio_layout
        )

        audio_format = (
            getattr(self, 'audio_format', Settings.DEFAULT_AUDIO_FORMAT.value)
            if audio_format is None else
            audio_format
        )

        writer = VideoWriter(output_filename)

        # TODO: This has to be dynamic according to the
        # video we are writing (?)
        writer.set_video_stream(
            codec_name = video_codec,
            fps = video_fps,
            size = video_size,
            pixel_format = video_pixel_format
        )
        
        writer.set_audio_stream(
            codec_name = audio_codec,
            fps = audio_sample_rate,
            layout = audio_layout,
            format = audio_format
        )

        # TODO: Maybe we need to reformat or something
        # if some of the values changed, such as fps,
        # audio sample rate, etc. (?)

        time_base = fps_to_time_base(video_fps)
        audio_time_base = fps_to_time_base(audio_sample_rate)

        for t in get_ts(0, self._end, video_fps):
            frame = self.get_video_frame_at(
                t = t,
                do_apply_filters = do_apply_video_filters
            )

            # TODO: What if 'frame' is None (?)
            if frame is None:
                print(f'   [ERROR] Frame not found at t:{float(t)}')
                continue

            writer.mux_video_frame(
                frame = frame
            )

            frame.time_base = time_base
            frame.pts = T(t, time_base).truncated_pts

            # TODO: Make this work
            # audio_pts = 0
            # for audio_frame in self.get_audio_frames_at_t(
            #     t = t,
            #     video_fps = video_fps,
            #     do_apply_filters = do_apply_audio_filters
            # ):
            #     # TODO: 'audio_frame' could be None or []
            #     # here if no audio channel
            #     if audio_frame is None:
            #         # TODO: Generate silence audio to cover the
            #         # whole video frame (?)
            #         pass
                
            #     # We need to adjust our output elements to be
            #     # consecutive and with the right values
            #     # TODO: We are using int() for fps but its float...
            #     audio_frame.time_base = audio_time_base
            #     audio_frame.pts = audio_pts

            #     # We increment for the next iteration
            #     audio_pts += audio_frame.samples

            #     writer.mux_audio_frame(audio_frame)

        writer.mux_video_frame(None)
        writer.mux_audio_frame(None)
        writer.output.close()

        return output_filename

class OpenGLCrossfadeTransitionMedia(_OpenglTransitionMedia):
    """
    A transition made with OpenGL that is a crossfade
    in between the frames.
    """

    def __init__(
        self,
        clip_a: _VideoMedia,
        clip_b: _VideoMedia,
        duration: float,
        # TODO: This has to be passed always from the editor
        opengl_context: Union['Context', None] = None,
    ):
        super().__init__(
            clip_a = clip_a,
            clip_b = clip_b,
            duration = duration,
            opengl_context = opengl_context
        )

        self.opengl_node: 'OpenglNodeBase' = CrossfadeTransitionNode(
            context = self.context,
            # TODO: Do not hardcode, please
            size = (1920, 1080),
        )
        """
        The OpenGL node that is actually the transition
        processor.
        """

class OpenGLDistortedCrossfadeTransitionMedia(_OpenglTransitionMedia):
    """
    A transition made with OpenGL that is a distorted
    crossfade in between the frames.
    """

    def __init__(
        self,
        clip_a: _VideoMedia,
        clip_b: _VideoMedia,
        duration: float,
        # TODO: This has to be passed always from the editor
        opengl_context: Union['Context', None] = None,
        intensity: float = 0.1,
    ):
        super().__init__(
            clip_a = clip_a,
            clip_b = clip_b,
            duration = duration,
            opengl_context = opengl_context
        )

        self.opengl_node: 'OpenglNodeBase' = DistortedCrossfadeTransitionNode(
            context = self.context,
            # TODO: Do not hardcode, please
            size = (1920, 1080),
            intensity = intensity
        )
        """
        The OpenGL node that is actually the transition
        processor.
        """

class OpenGLSlideTransitionMedia(_OpenglTransitionMedia):
    """
    A transition made with OpenGL that is a slide 
    between the frames.
    """

    def __init__(
        self,
        clip_a: _VideoMedia,
        clip_b: _VideoMedia,
        duration: float,
        # TODO: This has to be passed always from the editor
        opengl_context: Union['Context', None] = None,
        # TODO: This must be an Enum and handled also in
        # the 'yta_video_opengl' library
        direction: int = 0,
    ):
        super().__init__(
            clip_a = clip_a,
            clip_b = clip_b,
            duration = duration,
            opengl_context = opengl_context
        )

        # TODO: Do I need it here or just in the node
        # instance (?)
        self._direction: int = direction
        """
        The direction of the slide.
        """

        self.opengl_node: 'OpenglNodeBase' = SlideTransitionNode(
            context = self.context,
            # TODO: Do not hardcode, please
            size = (1920, 1080),
            direction = direction
        )
        """
        The OpenGL node that is actually the transition
        processor.
        """

class OpenGLCircleOpeningTransitionMedia(_OpenglTransitionMedia):
    """
    A transition made with OpenGL that is a circle
    growing from the middle of the video.
    """

    def __init__(
        self,
        clip_a: _VideoMedia,
        clip_b: _VideoMedia,
        duration: float,
        # TODO: This has to be passed always from the editor
        opengl_context: Union['Context', None] = None,
    ):
        super().__init__(
            clip_a = clip_a,
            clip_b = clip_b,
            duration = duration,
            opengl_context = opengl_context
        )

        self.opengl_node: 'OpenglNodeBase' = CircleOpeningTransitionNode(
            context = self.context,
            # TODO: Do not hardcode, please
            size = (1920, 1080),
            resolution = (1920, 1080),
        )
        """
        The OpenGL node that is actually the transition
        processor.
        """

class OpenGLCircleClosingTransitionMedia(_OpenglTransitionMedia):
    """
    A transition made with OpenGL that is a circle
    disappearing in the middle of the screen.
    """

    def __init__(
        self,
        clip_a: _VideoMedia,
        clip_b: _VideoMedia,
        duration: float,
        # TODO: This has to be passed always from the editor
        opengl_context: Union['Context', None] = None,
    ):
        super().__init__(
            clip_a = clip_a,
            clip_b = clip_b,
            duration = duration,
            opengl_context = opengl_context
        )

        self.opengl_node: 'OpenglNodeBase' = CircleClosingTransitionNode(
            context = self.context,
            # TODO: Do not hardcode, please
            size = (1920, 1080),
            resolution = (1920, 1080),
        )
        """
        The OpenGL node that is actually the transition
        processor.
        """

class OpenGLAlphaPediaTransitionMedia(_OpenglTransitionMedia):
    """
    A transition that joins 2 videos by applying
    another video as a mask, that is specifically
    built for this purpose and stored in the
    AlphaPediaYT channel.

    These videos are made with black and white
    colors that are transformed into an alpha
    channel according to the presence of that 
    white color and becoming a mask.
    """

    def __init__(
        self,
        clip_a: _VideoMedia,
        clip_b: _VideoMedia,
        # TODO: Maybe url instead (?)
        clip_mask: _VideoMedia,
        # The video has its own duration so we can
        # use it (if possible)
        duration: Union[float, None],
        # TODO: This has to be passed always from the editor
        opengl_context: Union['Context', None] = None,
    ):
        super().__init__(
            clip_a = clip_a,
            clip_b = clip_b,
            duration = duration,
            opengl_context = opengl_context
        )
        
        # TODO: I think we don't need it to be a
        # VideoOnTrack. As a Media is ok to get
        # the frame
        self._mask_clip = VideoOnTrack(
            media = clip_mask,
            start = 0
        )

        self.opengl_node: 'OpenglNodeBase' = AlphaPediaMaskTransitionNode(
            context = self.context,
            # TODO: Do not hardcode, please
            size = (1920, 1080),
        )
        """
        The OpenGL node that is actually the transition
        processor.
        """

    def get_video_frame_at(
        self,
        t: Union[int, float, Fraction],
        do_apply_filters: bool = False
    ) -> VideoFrame:
        """
        The `t` time moment provided must be a global
        time value pointing to a moment in the general
        timeline. That value will be transformed to the
        internal `t` value to get the frame.
        """
        # Test with OpenGL
        frame_a = self._clip_a.get_video_frame_at(t)
        frame_b = self._clip_b.get_video_frame_at(t)

        if (
            frame_a is None and
            frame_b is None
        ):
            print('Both None, wtf')
            #return None

        """
        There is a moment in which we are not in
        the transition section but on the clips
        so we just need to return the clip frames.
        """
        if frame_b is None:
            # Not transition time, just one clip
            out_frame = frame_a
            out_frame.pts = None
            out_frame.time_base = Fraction(1, 60)

            return out_frame
        
        if frame_a is None:
            # Not transition time, just one clip
            out_frame = frame_b
            out_frame.pts = None
            out_frame.time_base = Fraction(1, 60)

            return out_frame
        
        # Render loop
        t_progress = (t - self._start) / self.duration
        frame_a = frame_a.to_ndarray(format = 'rgb24').astype(np.float32)
        frame_b = frame_b.to_ndarray(format = 'rgb24').astype(np.float32)

        """
        Obtain the mask frame to apply in that moment, that
        must be calculated with the 't_progress'.
        """
        t_mask = t_progress * self._mask_clip.duration
        print(f't_mask: {str(t_mask)}')
        frame_mask = self._mask_clip.get_video_frame_at(t_mask).to_ndarray(format = 'rgb24').astype(np.float32)

        # TODO: Do we need the alpha (not rgb24)? Maybe to mix with
        # something else
        return self._process_frame(
            frame_a = frame_a,
            frame_b = frame_b,
            frame_mask = frame_mask,
            t_progress = t_progress
        )

    def _process_frame(
        self,
        # numpy array or texture
        frame_a: any,
        # numpy array or texture
        frame_b: any,
        # numpy array or texture
        frame_mask: any,
        t_progress: float,
    ):
        # TODO: We need to get the frame of the
        # 'frame_mask' for the 't_progress'

        frame = VideoFrame.from_ndarray(
            array = texture_to_frame(
                texture = self.opengl_node.process(
                    input_a = frame_a,
                    input_b = frame_b,
                    input_mask = frame_mask,
                    progress = t_progress
                ),
                do_include_alpha = False
            ).astype(np.uint8),
            format = 'rgb24'
        )
        # The 'pts' and that is not important here but...
        frame.pts = None
        frame.time_base = Fraction(1, 60)

        return frame


# TODO: Build more transitions
    

"""
Davinci Resolve has these 3 types of transition
strategies:
- Start on Cut → La transición empieza justo en el corte, extendiéndose hacia adelante.
- Center on Cut → La transición se centra en el corte (la mitad sobre el primer clip y la mitad sobre el segundo).
- End on Cut → La transición termina justo en el corte, extendiéndose hacia atrás.
"""