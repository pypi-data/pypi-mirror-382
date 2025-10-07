from yta_editor.track.media.abstract import _MediaOnTrackWithAudio, _MediaOnTrackWithVideo
from yta_editor.media.video import VideoFileMedia, VideoImageMedia, VideoColorMedia
from yta_validation.parameter import ParameterValidator
from quicktions import Fraction
from typing import Union


class VideoOnTrack(_MediaOnTrackWithAudio, _MediaOnTrackWithVideo):
    """
    A video media but positioned on a video
    track in the editor timeline.
    """

    def __init__(
        self,
        media: Union[VideoFileMedia, VideoImageMedia, VideoColorMedia],
        start: Union[int, float, Fraction] = 0.0
    ):
        ParameterValidator.validate_mandatory_instance_of('media', media, [VideoFileMedia, VideoImageMedia, VideoColorMedia])

        super().__init__(
            media = media,
            start = start
        )