from yta_editor.media.abstract import _Media
from yta_editor.sources.abstract import _AudioSource
from yta_editor.sources.audio import AudioFileSource, AudioNumpySource
from yta_editor.decorators import with_t_adjusted_to_media
from yta_editor.utils.effects import apply_audio_effects_to_frame_at_t
from yta_video_pyav.reader.filter.dataclass import GraphFilter
from yta_video_opengl.nodes import TimedNode
from yta_validation.parameter import ParameterValidator
from quicktions import Fraction
from typing import Union


class _AudioMedia(_Media):
    """
    Abstract class to be inherited by any
    media element.

    The media element is an element that
    includes a source and a 'start' and
    'end' values to be able to subclip that
    media source and use only the part we
    want to use.
    """

    def __init__(
        self,
        source: _AudioSource,
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None,
    ):
        super().__init__(
            source = source,
            start = start,
            end = end
        )

    def add_effect(
        self,
        effect: TimedNode
    ) -> '_AudioMedia':
        """
        Add the provided 'effect' to the audio.
        """
        ParameterValidator.validate_mandatory_instance_of('effect', effect, 'TimedNode')

        if not effect.is_audio_node:
            raise Exception('The provided "effect" is not an audio effect.')

        self._effects.add_effect(effect)
        
        return self
    
    @with_t_adjusted_to_media
    def get_audio_frames_at_t(
        self,
        t: Union[int, float, Fraction],
        video_fps: Union[int, float, Fraction]
    ):
        """
        Get the sequence of audio frames for a 
        given video 't' time moment, using the
        audio cache system.

        This is useful when we want to write a
        video frame with its audio, so we obtain
        all the audio frames associated to it
        (remember that a video frame is associated
        with more than 1 audio frame).
        """
        print(f'Getting audio frames from {str(float(t + self.start))} that is actually {str(float(t))}')
        for frame in self.source.get_audio_frames_at_t(t, video_fps):
            yield apply_audio_effects_to_frame_at_t(
                effects_stack = self._effects,
                frame = frame,
                t = t
            )

class AudioFileMedia(_AudioMedia):
    """
    An audio media that is read from an audio
    file and can be subclipped to a specific
    time range.
    """

    @property
    def copy(
        self
    ) -> 'AudioFileMedia':
        """
        Get a copy of this instance with the same
        source, time range and effects.
        """
        copy = AudioFileMedia._init_with_source(
            source = self.source,
            start = self.start,
            end = self.end
        )

        copy._effects = self._effects.copy

        return copy

    @property
    def duration(
        self
    ) -> Fraction:
        """
        The duration of the video.
        """
        return self.end - self.start
    
    @property
    def audio_fps(
        self
    ) -> Union[int, None]:
        """
        The frames per second of the audio.
        """
        return self.source.audio_fps
    
    @property
    def audio_codec_name(
        self
    ) -> Union[str, None]:
        """
        The name of the audio codec.
        """
        return self.source.audio_codec_name
    
    @property
    def audio_layout(
        self
    ) -> Union[str, None]:
        """
        The audio layout.
        """
        return self.source.audio_layout.name
    
    @property
    def audio_format(
        self
    ) -> Union[str, None]:
        """
        The audio format.
        """
        return self.source.audio_format.name
    
    @property
    def audio_time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the audio.
        """
        return self.source.audio_time_base
    
    def __init__(
        self,
        filename: str,
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None,
        # These are ffmpeg filters
        audio_filters: list[GraphFilter] = []
    ):
        super().__init__(
            source = AudioFileSource(
                filename = filename,
                audio_filters = audio_filters
            ),
            start = start,
            end = end
        )

    def add_audio_filter(
        self,
        filter: GraphFilter
    ) -> 'AudioFileMedia':
        """
        Add an audio filter to the list of filters
        to apply.
        """
        self.source.add_audio_filter(filter)

        return self

# TODO: Create 'AudioNumpyMedia'