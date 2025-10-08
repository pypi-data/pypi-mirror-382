from yta_editor.track.media.video import VideoOnTrack
from yta_editor.media.video import _VideoMedia
from yta_editor.media.transition.classes import AlphaBlendTransition
from yta_video_frame_time.t_fraction import get_ts, fps_to_time_base, T
from yta_video_pyav.writer import VideoWriter
from yta_video_pyav.settings import Settings
from yta_validation.parameter import ParameterValidator
from av.video.frame import VideoFrame
from quicktions import Fraction
from typing import Union

import numpy as np


class TransitionMedia:
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
        # TODO: Apply Union[AlphaBlendTransition, ...]
        transition: AlphaBlendTransition,
        duration: float,
    ):
        ParameterValidator.validate_subclass_of('clip_a', clip_a, _VideoMedia)
        ParameterValidator.validate_subclass_of('clip_b', clip_b, _VideoMedia)

        if (
            clip_a.duration < duration or
            clip_b.duration < duration
        ):
            raise Exception('The duration of one of the clips is smaller than the transition duration requested.')

        # TODO: Apply Union[AlphaBlendTransition, ...]
        self._transition: AlphaBlendTransition = transition
        """
        The configuration we want to apply in the transition.
        """
        self.duration: float = duration
        """
        The duration of the transition.
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

        # TODO: By now I'm forcing a simple crossfade
        # transition just to validate it works
        # TODO: This has to be more complex and also
        # using curves
        t_progress = (t - self._start) / self.duration
        print(f' ------->  T progress: {str(t_progress)}')

        # TODO: What about 'get_blend_factor_at_t' (?)

        result_frame = VideoFrame.from_ndarray(
            array = (
                self._transition.blend_frames(
                    frame_a = frame_a.to_ndarray(format = 'rgb24').astype(np.float32),
                    frame_b = frame_b.to_ndarray(format = 'rgb24').astype(np.float32),
                    t_progress = t_progress
                )
            ).astype(np.uint8),
            format = 'rgb24'
        )
        # The 'pts' and that is not important here but...
        result_frame.pts = None
        result_frame.time_base = Fraction(1, 60)

        return result_frame
    
    # def get_audio_frames_at(
    #     self,
    #     t: Union[int, float, Fraction],
    #     video_fps: Union[int, float, Fraction, None] = None,
    #     do_apply_filters: bool = True
    # ):
    #     """
    #     Get the sequence of audio frames for the 
    #     given video 't' time moment, using the
    #     audio cache system.

    #     This is useful when we want to write a
    #     video frame with its audio, so we obtain
    #     all the audio frames associated to it
    #     (remember that a video frame is associated
    #     with more than 1 audio frame).
    #     """
    #     frame_a = self._clip_a.get_audio_frames_at(t)
    #     frame_b = self._clip_b.get_video_frame_at(t)

    #     if (
    #         frame_a is None and
    #         frame_b is None
    #     ):
    #         print('Both None, wtf')
    #         #return None

    #     """
    #     There is a moment in which we are not in
    #     the transition section but on the clips
    #     so we just need to return the clip frames.
    #     """
    #     if frame_b is None:
    #         # Not transition time, just one clip
    #         out_frame = frame_a
    #         out_frame.pts = None
    #         out_frame.time_base = Fraction(1, 60)

    #         return out_frame
        
    #     if frame_a is None:
    #         # Not transition time, just one clip
    #         out_frame = frame_b
    #         out_frame.pts = None
    #         out_frame.time_base = Fraction(1, 60)

    #         return out_frame

    #     # TODO: By now I'm forcing a simple crossfade
    #     # transition just to validate it works
    #     # TODO: This has to be more complex and also
    #     # using curves
    #     t_progress = (t - self._start) / self.duration
    #     print(f' ------->  T progress: {str(t_progress)}')

    #     # TODO: What about 'get_blend_factor_at_t' (?)

    #     # TODO: How to mix the audio frames (?)
    #     raise Exception('Not ready yet')
    #     # numpy_frame_a = frame_a.to_ndarray(format = 'rgb24').astype(np.float32)
    #     # numpy_frame_b = frame_b.to_ndarray(format = 'rgb24').astype(np.float32)

    #     # result_frame = VideoFrame.from_ndarray(
    #     #     array = (
    #     #         # Replace by specific alpha blending strategy
    #     #         (1 - t_progress) * numpy_frame_a + t_progress * numpy_frame_b
    #     #     ).astype(np.uint8),
    #     #     format = 'rgb24'
    #     # )
    #     # # The 'pts' and that is not important here but...
    #     # result_frame.pts = None
    #     # result_frame.time_base = Fraction(1, 60)

    #     # return result_frame
    
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

"""
Davinci Resolve has these 3 types of transition
strategies:
- Start on Cut → La transición empieza justo en el corte, extendiéndose hacia adelante.
- Center on Cut → La transición se centra en el corte (la mitad sobre el primer clip y la mitad sobre el segundo).
- End on Cut → La transición termina justo en el corte, extendiéndose hacia atrás.
"""