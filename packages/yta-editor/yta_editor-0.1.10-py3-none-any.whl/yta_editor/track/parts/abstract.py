from yta_editor.utils.silence import generate_silent_frames
from yta_editor.utils.frame_wrapper import AudioFrameWrapped, VideoFrameWrapped
from yta_editor.utils.frame_generator import VideoFrameGenerator
from yta_video_frame_time.t_fraction import fps_to_time_base
from yta_validation.parameter import ParameterValidator
from quicktions import Fraction
from typing import Union
from abc import ABC


NON_LIMITED_EMPTY_PART_END = 999
"""
A value to indicate that the empty part
has no end because it is in the last
position and there is no video after it.
"""

class _Part(ABC):
    """
    Abstract class to represent an element
    that is on the track, that can be an
    empty space or a vide or audio. This
    class must be inherited by our own
    custom part classes.
    """

    @property
    def is_empty_part(
        self
    ) -> bool:
        """
        Flag to indicate if the part is an empty part,
        which means that there is no media associated
        but an empty space.
        """
        return self.media is None

    def __init__(
        self,
        track: Union['AudioTrack', 'VideoTrack'],
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction],
        media: Union['AudioOnTrack', 'VideoOnTrack', None] = None
    ):
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_mandatory_positive_number('end', end, do_include_zero = False)
        ParameterValidator.validate_instance_of('media', media, ['AudioOnTrack', 'VideoOnTrack'])

        self._track: Union['AudioTrack', 'VideoTrack'] = track
        """
        The instance of the track this part belongs
        to.
        """
        self.start: Fraction = Fraction(start)
        """
        The start 't' time moment of the part.
        """
        self.end: Fraction = Fraction(end)
        """
        The end 't' time moment of the part.
        """
        self.media: Union['AudioOnTrack', 'VideoOnTrack', None] = media
        """
        The media associated, if existing, or
        None if it is an empty space that we need
        to fulfill.
        """

class _PartWithAudio(_Part):
    """
    TODO: Explain
    """

    @property
    def _silent_frames(
        self
    ) -> list[AudioFrameWrapped]:
        """
        *For internal use only*

        The silent frames we need to fulfill the
        space when an empty part. Property to
        avoid creating these silent frames again
        and again.
        """
        if not hasattr(self, '__silent_frames'):
            self.__silent_frames = generate_silent_frames(
                video_fps = self._track.fps,
                audio_fps = self._track.audio_fps,
                audio_samples_per_frame = self._track.audio_samples_per_frame,
                # TODO: Where do this 2 formats come from (?)
                layout = self._track.audio_layout,
                format = self._track.audio_format
            )

        return self.__silent_frames

    def __init__(
        self,
        track: Union['AudioTrack', 'VideoTrack'],
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction],
        media: Union['AudioOnTrack', 'VideoOnTrack', None] = None
    ):
        ParameterValidator.validate_instance_of('media', media, ['AudioOnTrack', 'VideoOnTrack'])

        super().__init__(
            track = track,
            start = start,
            end = end,
            media = media
        )

    def get_audio_frames_at_t(
        self,
        t: Union[int, float, Fraction],
        video_fps = Union[int, float, Fraction]
    ):
        """
        Iterate over all the audio frames that
        exist at the time moment 't' provided.
        """
        frames = []
        if not self.is_empty_part:
            # TODO: What do we do in this case (?)
            frames = list(self.media.get_audio_frames_at(t, video_fps))

            if len(frames) == 0:
                print(f'   [ERROR] Audio frame {str(float(t))} was not obtained')
            else:
                frames = [
                    AudioFrameWrapped(
                        frame = frame,
                        is_from_empty_part = False
                    )
                    for frame in frames
                ]

        # This could be because is empty part or
        # because we couldn't obtain the frames
        frames = (
            self._silent_frames
            if len(frames) == 0 else
            frames
        )

        for frame in frames:
            yield frame

class _PartWithVideo(_Part):
    """
    TODO: Explain
    """

    @property
    def _frame_not_found(
        self
    ):
        """
        *For internal use only*

        The frame we should send when we didn't
        obtain a frame from a source that should
        be available. Property to avoid creating
        this frame again and again.

        TODO: This should not happen, it is an
        internal way to point an error.
        """
        if not hasattr(self, '__empty_frame'):
            self.__frame_not_found = VideoFrameGenerator.background.full_red(
                size = self._track.size,
                time_base = fps_to_time_base(self._track.fps)
            )

        return self.__frame_not_found

    @property
    def _empty_frame(
        self
    ):
        """
        *For internal use only*

        The frame we should send when an empty
        part is playing. Property to avoid
        creating this frame again and again.
        """
        if not hasattr(self, '__empty_frame'):
            self.__empty_frame = VideoFrameGenerator.background.full_black(
                size = self._track.size,
                time_base = fps_to_time_base(self._track.fps),
                transparency = 1.0
            )

        return self.__empty_frame

    def __init__(
        self,
        track: 'VideoTrack',
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction],
        media: Union['VideoOnTrack', None] = None
    ):
        ParameterValidator.validate_instance_of('media', media, 'VideoOnTrack')

        super().__init__(
            track = track,
            start = start,
            end = end,
            media = media
        )

    def get_video_frame_at_t(
        self,
        t: Union[int, float, Fraction]
    ) -> 'VideoFrameWrapped':
        """
        Get the frame that must be displayed at 
        the given 't' time moment.
        """
        is_from_empty_part = False
        if self.is_empty_part == True:
            frame = self._empty_frame

            is_from_empty_part = True
        else:
            # TODO: This can be None, why? I don't know...
            frame = self.media.get_video_frame_at(t)

            if frame is None:
                print(f'   [ERROR] Frame {str(float(t))} was not obtained')

            frame = (
                # I'm using a red full frame to be able to detect
                # fast the frames that were not available, but
                # I need to find the error and find a real solution
                # TODO: This shouldn't happen, its an error
                self._frame_not_found
                if frame is None else
                frame
            )

        # TODO: What about the 'format' (?)
        # TODO: Maybe I shouldn't set the 'time_base'
        # here and do it just in the Timeline 'render'
        #return get_black_background_video_frame(self._track.size)
        # TODO: This 'time_base' maybe has to be related
        # to a Timeline general 'time_base' and not the fps
        frame = VideoFrameWrapped(
            frame = frame,
            is_from_empty_part = is_from_empty_part
        )

        # TODO: This should not happen because of
        # the way we handle the videos here but the
        # video could send us a None frame here, so
        # do we raise exception (?)
        if frame._frame is None:
            #frame = get_black_background_video_frame(self._track.size)
            # TODO: By now I'm raising exception to check if
            # this happens or not because I think it would
            # be malfunctioning
            raise Exception(f'Video is returning None video frame at t={str(t)}.')
        
        """
        The 'track' (because of the 'timeline' it belongs
        to) has a size, so we must respect, so we need to
        use a strategy to make it fit the desired size.
        """
        # TODO: Maybe this sould be done in the 'timeline'
        # that combines the frames and not here...
        return frame