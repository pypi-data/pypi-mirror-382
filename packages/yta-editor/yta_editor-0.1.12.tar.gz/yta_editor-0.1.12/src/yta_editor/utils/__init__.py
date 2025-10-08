from yta_constants.ffmpeg import FfmpegAudioLayout, FfmpegAudioFormat, FfmpegPixelFormat
from yta_validation.parameter import ParameterValidator
from av.audio.frame import AudioFrame
from av.audio.layout import AudioLayout
from av.audio.stream import AudioStream
from av.video.stream import VideoStream
from av.video.frame import VideoFrame
from quicktions import Fraction
from av import open as av_open
from typing import Union

import numpy as np


class _AlphaUtils:
    """
    General class to include some utils related
    to alpha channel and the pyav library.
    """

    @staticmethod
    def file_has_alpha_layer(
        filename: str
    ) -> bool:
        """
        Check if the video file with the given 'filename'
        has alpha layer or not, that is defined by an
        'a' in the frame format name. This will test the
        first frame of the video and return a result.

        This doesn't mean that there are transparent
        pixels on the video, just the presence of the
        alpha layer.
        """
        return _AlphaUtils.videoframe_has_alpha_layer(next(_VideoUtils.iter_frames(filename)))

    @staticmethod
    def videoframe_has_alpha_layer(
        frame: VideoFrame
    ) -> bool:
        """
        Check if the provided 'frame' pyav VideoFrame
        has alpha layer or not, that is defined by an
        'a' in the frame format name.
        
        This doesn't mean that some pixel is
        transparent, it only means that there is an
        alpha layer, but the frame could be completely
        opaque.

        The code:
        - `'a' in frame.format.name`
        """
        ParameterValidator.validate_mandatory_instance_of('frame', frame, VideoFrame)

        return 'a' in frame.format.name
    
    @staticmethod
    def numpy_videoframe_has_transparent_pixels(
        frame: 'np.ndarray'
    ) -> bool:
        """
        Check if the provided numpy array has alpha
        pixels or not. If the provided numpy array
        doesn't include an alpha layer the result
        will be False.
        """
        return (
            frame.ndim == 3 and
            frame.shape[2] > 3 and
            np.any(frame[..., 3] < 255)
        )
    
    @staticmethod
    def videoframe_has_transparent_pixels(
        frame: VideoFrame
    ) -> bool:
        """
        Check if the provided frame has alpha pixels
        or not.
        """
        return _AlphaUtils.numpy_videoframe_has_transparent_pixels(frame.to_ndarray(format = 'rgba'))

    @staticmethod
    def file_has_transparent_pixels(
        filename: str
    ) -> bool:
        """
        Check if the video with the provided 'filename'
        has some transparent (at least partially) alpha
        pixels by decoding the frames until finding one
        that has some transparency.

        This process is slow because it will decode the
        whole video until finding some transparent pixel
        (if existing).
        """
        for frame in _VideoUtils.iter_frames(filename):
            if not _AlphaUtils.videoframe_has_alpha_layer(frame):
                break
            
            # Check if alpha channel has some transparency
            if _AlphaUtils.videoframe_has_transparent_pixels(frame):
                return True
            
        return False
    
class _VideoFrameUtils:
    """
    *For internal use only*

    Class to wrap functionality related to video
    frames.
    """
    
    def copy(
        video_frame: VideoFrame
    ) -> 'VideoFrame':
        """
        Create a copy of the provided VideoFrame
        instance. This is similar to .copy().
        """
        return VideoFrame.from_ndarray(
            array = video_frame.to_ndarray(format = video_frame.format.name),
            format = video_frame.format.name
        )
    
    @staticmethod
    def combine_videoframes_with_alpha_layer(
        top_frame: VideoFrame,
        bottom_frame: VideoFrame,
        pixel_format: Union[FfmpegPixelFormat, None] = None
    ) -> VideoFrame:
        """
        Combine the provided 'top_frame' and
        'bottom_frame' transforming them into a
        RGBA and uint8 numpy array.

        The pixel format will be the provided as
        the 'pixel_format' parameter, or the one
        the 'top_frame' has.
        """
        # TODO: What if the size is not the same (?)
        # TODO: What if no alpha layer in the frames (?)
        pixel_format = (
            top_frame.format.name
            if pixel_format is None else
            FfmpegPixelFormat.to_enum(pixel_format).value
        )

        return VideoFrame.from_ndarray(
            array = _VideoFrameUtils.combine_numpy_videoframes_with_alpha_layer(
                top_frame = top_frame.to_ndarray(format = FfmpegPixelFormat.RGBA.value),
                bottom_frame = bottom_frame.to_ndarray(format = FfmpegPixelFormat.RGBA.value)
            ),
            format = pixel_format
        )

    @staticmethod
    def combine_numpy_videoframes_with_alpha_layer(
        top_frame: np.ndarray,
        bottom_frame: np.ndarray
    ) -> np.ndarray:
        """
        Combine 2 RGBA frames, that must be (h, w, 4)
        and uint8, with alpha blending. Useful to
        combine video frames with alpha blending.

        This method returns the new combined frame.
        """
        # To float in [0, 1] range
        top_frame_rgb = top_frame[..., :3].astype(np.float32) / 255.0
        bottom_frame_rgb = bottom_frame[..., :3].astype(np.float32) / 255.0
        top_frame_alpha = top_frame[..., 3:].astype(np.float32) / 255.0
        bottom_frame_alpha = bottom_frame[..., 3:].astype(np.float32) / 255.0

        # Alpha blending
        output_alpha = top_frame_alpha + bottom_frame_alpha * (1 - top_frame_alpha)
        # Avoid division by zero
        output_rgb = (top_frame_rgb * top_frame_alpha + bottom_frame_rgb * bottom_frame_alpha * (1 - top_frame_alpha)) / np.clip(output_alpha, 1e-6, 1.0)

        # Back to uint8
        output_frame = np.zeros_like(top_frame, dtype = np.uint8)
        output_frame[..., :3] = (output_rgb * 255).astype(np.uint8)
        output_frame[..., 3:] = (output_alpha * 255).astype(np.uint8)

        return output_frame
    
class _VideoUtils:
    """
    *For internal use only*

    Class to wrap some utils related to video.
    """

    alpha: _AlphaUtils = _AlphaUtils
    """
    Information about the alpha channel.
    """
    frame: _VideoFrameUtils = _VideoFrameUtils
    """
    Utils related to video frames.
    """

    @staticmethod
    def iter_frames(
        filename: str
    ):
        """
        Iterator over the video frames of the file
        with the given 'filename'.
        """
        container = av_open(file = filename)
        video_stream = (
            container.streams.video[0]
            if container.streams.video else
            None
        )

        if video_stream is None:
            raise Exception(f'No video stream found in "{filename}" file.')
        
        for frame in _iter_frames(
            stream = video_stream
        ):
            yield frame

        return
    
class _AudioFormatUtils:
    """
    *For internal use only*

    Class to wrap some utils related to audio
    format.
    """

    @staticmethod
    def to_dtype(
        audio_format: str
    ) -> Union[np.dtype, None]:
        """
        Transform the given 'audio_format' into
        the corresponding numpy dtype value. If
        the 'audio_format' is not accepted this
        method will return None.

        This method must be used when we are
        building the numpy array that will be 
        used to build a pyav audio frame because
        the pyav 'audio_format' need a specific
        np.dtype to be built.

        For example, 's16' will return 'np.int16'
        and 'fltp' will return 'np.float32'.
        """
        return {
            # Integers and signed
            FfmpegAudioFormat.U8.value:   np.uint8,   # unsigned 8-bit
            FfmpegAudioFormat.S16.value:  np.int16,   # signed 16-bit
            FfmpegAudioFormat.S32.value:  np.int32,   # signed 32-bit

            # Floats
            FfmpegAudioFormat.FLT.value:  np.float32, # 32-bit float (interleaved)
            FfmpegAudioFormat.FLTP.value: np.float32, # 32-bit float (planar)
            FfmpegAudioFormat.DBL.value:  np.float64, # 64-bit float (interleaved)
            FfmpegAudioFormat.DBLP.value: np.float64, # 64-bit float (planar)

            # Very deep extensions
            FfmpegAudioFormat.S64.value:  np.int64,   # signed 64-bit
            FfmpegAudioFormat.S64P.value: np.int64,   # signed 64-bit (planar)

            # Integer planars (each channel separate)
            FfmpegAudioFormat.U8P.value:  np.uint8,
            FfmpegAudioFormat.S16P.value: np.int16,
            FfmpegAudioFormat.S32P.value: np.int32,
        }.get(FfmpegAudioFormat.to_enum(audio_format).value, None)

class _AudioFrameUtils:
    """
    *For internal use only*

    Class to wrap some utils related to audio
    frames.
    """

    @staticmethod
    def trim(
        frame: AudioFrame,
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction],
        time_base: Fraction
    ) -> AudioFrame:
        """
        Trim an audio frame to obtain the part between
        [start, end), that is provided in seconds.
        """
        # (channels, n_samples)
        samples = frame.to_ndarray()  
        n_samples = samples.shape[1]

        # In seconds
        frame_start = frame.pts * float(time_base)
        frame_end = frame_start + (n_samples / frame.sample_rate)

        # Overlapping 
        cut_start = max(frame_start, float(start))
        cut_end = min(frame_end, float(end))

        if cut_start >= cut_end:
            # No overlapping
            return None  

        # To sample indexes
        start_index = int(round((cut_start - frame_start) * frame.sample_rate))
        end_index = int(round((cut_end - frame_start) * frame.sample_rate))

        new_frame = AudioFrame.from_ndarray(
            # end_index is not included: so [start, end)
            array = samples[:, start_index:end_index],
            format = frame.format,
            layout = frame.layout
        )

        # Set needed attributes
        new_frame.sample_rate = frame.sample_rate
        new_frame.time_base = time_base
        new_frame.pts = int(round(cut_start / float(time_base)))

        return new_frame
    
    @staticmethod
    def silent(
        sample_rate: int,
        number_of_samples: int = 1024,
        layout = FfmpegAudioLayout.STEREO.value,
        format = FfmpegAudioFormat.S16.value,
        pts: Union[int, None] = None,
        time_base: Union[Fraction, None] = None
    ) -> AudioFrame:
        """
        Get an audio frame that is completely silent.
        This is useful when we want to fill the empty
        parts of our tracks.
        """
        layout = FfmpegAudioLayout.to_enum(layout).value
        format = FfmpegAudioFormat.to_enum(format).value

        dtype = _AudioFormatUtils.to_dtype(format)

        if dtype is None:
            raise Exception(f'The format "{format}" is not accepted.')

        number_of_channels = len(AudioLayout(layout).channels)

        # TODO: I leave these comments below because
        # I'm not sure what is true and what is not
        # so, until it is more clear... here it is:
        # For packed (or planar) formats we apply:
        # (1, samples * channels). This is the same
        # amount of data but planar, in 1D only
        # TODO: This wasn't in the previous version
        # and it was working, we were sending the
        # same 'number_of_samples' even when 'fltp'
        # that includes the 'p'
        # TODO: This is making the audio last 2x
        # if 'p' in format:
        #     number_of_samples *= number_of_channels

        silent_numpy_array = np.zeros(
            shape = (number_of_channels, number_of_samples),
            dtype = dtype
        )

        return _AudioFrameUtils.from_numpy_audioframe(
            frame = silent_numpy_array,
            sample_rate = sample_rate,
            layout = layout,
            format = format,
            pts = pts,
            time_base = time_base
        )
    
    @staticmethod
    def from_numpy_audioframe(
        frame: np.ndarray,
        sample_rate: int,
        layout: str = FfmpegAudioLayout.STEREO.value,
        format: str = FfmpegAudioFormat.S16.value,
        pts: Union[int, None] = None,
        time_base: Union[Fraction, None] = None
    ) -> AudioFrame:
        """
        Transform the given numpy audio 'frame' into a
        pyav audio frame with the given 'sample_rate',
        'layout' and 'format, and also the 'pts
        and/or 'time_base' if provided.
        """
        layout = FfmpegAudioLayout.to_enum(layout).value
        format = FfmpegAudioFormat.to_enum(format).value

        frame = AudioFrame.from_ndarray(
            array = frame,
            format = format,
            layout = layout
        )

        frame.sample_rate = sample_rate

        if pts is not None:
            frame.pts = pts

        if time_base is not None:
            frame.time_base = time_base

        return frame
    
class _AudioUtils:
    """
    *For internal use only*

    Class to wrap some utils related to audio.
    """

    frame: _AudioFrameUtils = _AudioFrameUtils
    """
    Utils related to audio frames.
    """
    format: _AudioFormatUtils = _AudioFormatUtils
    """
    Utils related to audio format.
    """

    @staticmethod
    def iter_frames(
        filename: str
    ):
        """
        Iterator over the audio frames of the file
        with the given 'filename'.
        """
        container = av_open(file = filename)
        audio_stream = (
            container.streams.audio[0]
            if container.streams.audio else
            None
        )

        if audio_stream is None:
            raise Exception(f'No audio stream found in "{filename}" file.')
        
        for frame in _iter_frames(
            stream = audio_stream
        ):
            yield frame

        return
    
class VideoUtils:
    """
    Class to wrap information about a video, to
    detect alpha pixels, etc., and also the audio.
    """

    video: _VideoUtils = _VideoUtils
    """
    Utils related to video.
    """
    audio: _AudioUtils = _AudioUtils
    """
    Utils related to audio.
    """

def _iter_frames(
    stream: Union['VideoStream', 'AudioStream']
):
    """
    Iterator over the video frames of the video
    with the given 'filename'.
    """
    for packet in stream.container.demux(stream):
        for frame in packet.decode():
            yield frame

    # Some frames can be retained in the demuxer
    for frame in stream.decode():
        yield frame

    return