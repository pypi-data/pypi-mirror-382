from yta_editor.track.parts.abstract import _PartWithAudio, _PartWithVideo
from yta_validation.parameter import ParameterValidator
from quicktions import Fraction
from typing import Union


class _VideoPart(_PartWithAudio, _PartWithVideo):
    """
    Class to represent an element that is on the
    track, that can be an empty space or a video.
    """

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