from yta_editor.track.parts.abstract import _PartWithAudio
from yta_validation.parameter import ParameterValidator
from quicktions import Fraction
from typing import Union


class _AudioPart(_PartWithAudio):
    """
    Class to represent an element that is on the
    track, that can be an empty space or an audio.
    """

    def __init__(
        self,
        track: 'AudioTrack',
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction],
        media: Union['AudioOnTrack', None] = None
    ):
        ParameterValidator.validate_instance_of('media', media, 'AudioOnTrack')

        super().__init__(
            track = track,
            start = start,
            end = end,
            media = media
        )