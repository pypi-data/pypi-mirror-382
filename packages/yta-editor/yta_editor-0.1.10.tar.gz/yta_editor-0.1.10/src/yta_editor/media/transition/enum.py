from yta_constants.enum import YTAEnum as Enum

import numpy as np


class AlphaBlendingMethod(Enum):
    """
    Class to wrap teh functionality related to
    alpha blending.

    These alpha blending methods are made with
    numpy and using CPU.
    """

    CROSSFADE = 'crossfade'
    WIPE_HORIZONTAL = 'wipe_horizontal'
    WIPE_VERTICAL = 'wipe_vertical'
    WIPE_DIAGONAL = 'wipe_diagonal'
    CIRCLE = 'circle'

    def blend_frames(
        self,
        frame_a: 'np.ndarray',
        frame_b: 'np.ndarray',
        # TODO: Rename this 't_progress' maybe (?)
        t_progress: float
    ) -> 'np.ndarray':
        """
        Blend the provided 'frame_a' and 'frame_b' with this
        method and obtain the result frame that will be
        returned.
        """
        frame = frame_a

        if self == AlphaBlendingMethod.CROSSFADE:
            frame = (1 - t_progress) * frame_a + t_progress * frame_b
        elif self == AlphaBlendingMethod.WIPE_HORIZONTAL:
            w = frame_a.shape[1]
            mask = np.linspace(0, 1, w)[None, :, None]

            if True:
                # TODO: This smooth border can be set in the other
                # wipes, so maybe we should add it
                # Wipe with smooth border
                fade_width = 0.1  # border width (in [0.0, 1.0])
                mask = np.clip((t_progress - mask) / fade_width, 0, 1)
            else:
                # Normal wipe
                mask = (mask < t_progress).astype(np.float32)

            # From left to right by default
            if True:
                # From right to left instead
                mask = np.flip(mask, axis = 0)

            frame = frame_a * (1 - mask) + frame_b * mask
        elif self == AlphaBlendingMethod.WIPE_VERTICAL:
            h = frame_a.shape[0]
            mask = np.linspace(0, 1, h)[:, None, None]
            mask = (mask < t_progress).astype(np.float32)

            # From top to bottom by default
            if True:
                # From bottom to top instead
                mask = np.flip(mask, axis = 0)

            frame = frame_a * (1 - mask) + frame_b * mask
        elif self == AlphaBlendingMethod.WIPE_DIAGONAL:
            h, w = frame_a.shape[:2]
            x = np.linspace(0, 1, w)[None, :, None]
            y = np.linspace(0, 1, h)[:, None, None]

            if True:
                # To change the direction
                mask = ((1 - x) + y) / 2

            # Combinamos ambos ejes: suma (↘) o resta (↗)
            mask = (x + y) / 2  # rango de 0 a 1
            mask = (mask < t_progress).astype(np.float32)

            frame = frame_a * (1 - mask) + frame_b * mask
        elif self == AlphaBlendingMethod.CIRCLE:
            h, w, _ = frame_a.shape
            Y, X = np.ogrid[:h, :w]
            cx, cy = w // 2, h // 2
            r = np.sqrt((X - cx)**2 + (Y - cy)**2)
            mask = (r < t_progress * max(cx, cy)).astype(np.float32)[..., None]

            frame = frame_a * (1 - mask) + frame_b * mask

        return frame

class TransitionType(Enum):
    """
    The type of transitions we can handle.
    """

    SIMPLE_ALPHA_BLENDING: str = 'simple_alpha_blending'
    """
    A simple alpha blending that is just blending
    the frames with the alpha blending strategy
    chosen.
    """
    VIDEO_ALPHA_BLENDING: str ='video_alpha_blending'
    """
    An alpha transition video is used to be applied
    as alpha layer to join the frames.
    """
    # TODO: Add more