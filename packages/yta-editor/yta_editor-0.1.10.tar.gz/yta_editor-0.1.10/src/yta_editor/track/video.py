"""
The video track module.
"""
from yta_editor.track.parts.video import _VideoPart
from yta_editor.track.media.video import VideoOnTrack
from yta_editor.track.abstract import _TrackWithAudio, _TrackWithVideo


class VideoTrack(_TrackWithVideo, _TrackWithAudio):
    """
    Class to represent a track in which we place
    videos to build a video project.
    """

    def __init__(
        self,
        index: int,
        size: tuple[int, int],
        fps: float,
        audio_fps: float,
        audio_samples_per_frame: int,
        audio_layout: str,
        audio_format: str
    ):
        # super().__init__(
        #     index = index,
        #     size = size,
        #     fps = fps,
        #     audio_fps = audio_fps,
        #     audio_samples_per_frame = audio_samples_per_frame,
        #     audio_layout = audio_layout,
        #     audio_format = audio_format
        # )
        _TrackWithVideo.__init__(
            self,
            index = index,
            size = size,
            fps = fps
        )
        _TrackWithAudio.__init__(
            self,
            index = index,
            fps = fps,
            audio_fps = audio_fps,
            audio_samples_per_frame = audio_samples_per_frame,
            audio_layout = audio_layout,
            audio_format = audio_format
        )
        
    def _make_part(
        self,
        **kwargs
    ):
        return _VideoPart(**kwargs)
    
    def _make_media_on_track(
        self,
        **kwargs
    ):
        return VideoOnTrack(**kwargs)