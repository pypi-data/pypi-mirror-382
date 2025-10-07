from yta_video_opengl.effects import EffectsStack
from yta_validation.parameter import ParameterValidator
from quicktions import Fraction
from typing import Union
from abc import ABC, abstractmethod


class _Media(ABC):
    """
    Abstract class to be inherited by any
    media element.

    The media element is an element that
    includes a source and a 'start' and
    'end' values to be able to subclip that
    media source and use only the part we
    want to use.
    """

    @property
    @abstractmethod
    def copy(
        self
    ) -> '_Media':
        """
        Get a copy of this instance with the same
        source, time range and effects.
        """
        pass

    @property
    def duration(
        self
    ) -> Fraction:
        """
        The duration of the media, that can be
        shorter than the source duration if the
        user requested it.

        The formula:
        - `self.end - self.start`
        """
        return self.end - self.start
    
    @property
    def time_remaining_until_start(
        self
    ) -> Fraction:
        """
        The time remaining at the begining of this
        Media source due to the 'start' provided to
        this instance.

        The source will always start on 0, so the
        actual start we use in this Media (maybe 2)
        is also the remaining time we didn't use at
        the begining (the first 2 seconds in this
        same example).

        This value can be useful for transitions.

        The formula:
        - `self.start`
        """
        return self.start
    
    @property
    def time_remaining_since_end(
        self
    ) -> Fraction:
        """
        The time remaining at the end of this Media
        source due to the 'end' provided to this
        instance.

        The source has its own duration, but maybe
        the 'end' we use is 2 seconds before that
        actual end moment, so the time remaining
        (that we didn't use) at the end of the source
        is the actual source duration minus the 'end'
        we provided here (2 seconds in this example I
        said).

        This value can be useful for transitions.

        The formula:
        - `self.source.duration - self.end`
        """
        return self.source.duration - self.end

    def __init__(
        self,
        source: Union['AudioFileSource', 'AudioNumpySource', 'VideoFileSource', 'VideoColorSource', 'VideoImageSource', 'VideoNumpySource'],
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None,
    ):
        self.source: Union['AudioFileSource', 'AudioNumpySource', 'VideoFileSource', 'VideoColorSource', 'VideoImageSource', 'VideoNumpySource'] = source
        """
        The source of this media element that
        is the entity from which we can obtain
        the frames.
        """
        self._effects: EffectsStack = EffectsStack()
        """
        The effects we want to apply on the
        media.
        """
        self.start: Fraction
        """
        The time moment 't' in which the media
        should start being played/displayed.
        """
        self.end: Union[Fraction, None]
        """
        The time moment 't' in which the media
        should end being played/displayed.
        """
        
        # Set 'start' and 'end'
        self.set_time_range(start, end)

    def set_time_range(
        self,
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction, None] = None,
    ) -> '_Media':
        """
        Set the media 'start' and 'end' time
        moments range from the original source
        that will be played/displayed.

        - If `end = None`, the source duration
        (if available) will be set.
        - If `end > source.duration` it will be
        replaced by the source duration value.
        """
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_positive_number('end', end, do_include_zero = False)

        self.start: Fraction = Fraction(start)
        self.end: Union[Fraction, None] = Fraction(
            # TODO: Is this 'end' ok (?)
            self.source.duration
            if (
                end is None or
                (
                    self.source.duration is not None and
                    end > self.source.duration
                )
            ) else
            end
        )

        # If the source has a duration, the 'start'
        # and 'end' must be valid
        if self.source.duration is not None:
            if (
                self.start >= self.source.duration and
                self.end >= self.source.duration
            ):
                raise Exception(f'The provided "start" and "end" are invalid values considering the real media duration of {str(float(self.source.duration))}s')
            
            if self.end <= self.start:
                raise Exception('The "end" value cannot be equal or smaller than the "start" value.')
            
            self.end = (
                self.source.duration
                if self.end > self.source.duration else
                self.end
            )

        return self
    
    # TODO: This method has been created
    # to be inherited by the other classes
    # and being able to copy the instance
    # properly by using the same 'source'
    # reference and creating not a new one
    @classmethod
    def _init_with_source(
        cls,
        source: Union['AudioFileSource', 'AudioNumpySource', 'VideoFileSource', 'VideoColorSource', 'VideoImageSource', 'VideoNumpySource'],
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None
    ):
        """
        *For internal use only*

        Alternative '__init__' to create the
        instance from the 'source' directly. This
        method must be called by the specific
        implementations of this abstract class
        to be able to instantiate them directly
        from the 'source' to make copies.

        We created this method to avoid generating
        a new 'source' instance but preserving the
        same reference.
        """
        # Create new instance skipping '__init__'
        instance = cls.__new__(cls)
        super(cls, instance).__init__(
            source = source,
            start = start,
            end = end
        )

        return instance

