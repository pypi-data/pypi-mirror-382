from yta_editor.track.media.abstract import _MediaOnTrackWithAudio
from yta_editor.media.audio import AudioFileMedia
from yta_validation.parameter import ParameterValidator
from quicktions import Fraction
from typing import Union


class AudioOnTrack(_MediaOnTrackWithAudio):
    """
    An audio media but positioned on an audio
    track in the editor timeline.
    """

    def __init__(
        self,
        media: AudioFileMedia,
        start: Union[int, float, Fraction] = 0.0
    ):
        ParameterValidator.validate_mandatory_instance_of('media', media, AudioFileMedia)

        super().__init__(
            media = media,
            start = start
        )

