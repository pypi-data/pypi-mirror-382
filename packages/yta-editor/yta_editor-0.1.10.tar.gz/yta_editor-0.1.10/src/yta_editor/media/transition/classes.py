"""
This module is working with the CPU and numpy
to handle different transitions.
"""
from yta_editor.media.transition.enum import AlphaBlendingMethod
from abc import ABC, abstractmethod

import numpy as np


# TODO: What about the audio (?)
class Transition(ABC):
    """
    The abstract class of the transition concept that
    will include the information, type and mode to
    blend the frames.

    This is not a MediaTransition but the configuration
    and specifications to implement one.

    This transition uses numpy and CPU.
    """

    @abstractmethod
    def blend_frames(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        # TODO: What if we receive 't' instead (?)
        # t: float
        t_progress: float
    ) -> np.ndarray:
        """
        Get the frame that is the result of applying the
        provided `t_progress` to the transition configuration.
        """
        pass

    """
    TODO: I think I need a 'blend_audio_frames' method to
    also mix the audio frames to obtain the expected result,
    and maybe I need to split it in Video and Audio 
    transitions.
    """

# TODO: Maybe move this to other file
class AlphaBlendTransition(Transition):
    """
    Transition that will blend the frames with a fixed
    logic defined in code to blend the frames.

    This transition uses numpy and CPU.
    """

    def __init__(
        self,
        alpha_blending_method: AlphaBlendingMethod,
    ):
        alpha_blending_method = AlphaBlendingMethod.to_enum(alpha_blending_method)

        self.alpha_blending_method: AlphaBlendingMethod = alpha_blending_method
        """
        The alpha blending method we want to apply in the
        transition, if needed.
        """

    def blend_frames(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        # TODO: What if we receive 't' instead (?)
        # t: float
        t_progress: float
    ) -> np.ndarray:
        """
        Get the frame that is the result of applying the
        provided `t_progress` to the transition configuration.
        """
        # TODO: Should I receive the 't' or the calculated
        # value (?)
        return self.alpha_blending_method.blend_frames(
            frame_a = frame_a,
            frame_b = frame_b,
            t_progress = t_progress
        )
    
class SlideTransition(Transition):
    """
    Transition that will move one video out
    of the screen and will make the other one
    appear from the opposite side.

    This transition uses numpy and CPU.
    """

    def __init__(
        self,
        # TODO: Apply Enum
        direction: str = 'left'
    ):
        self.direction: str = direction
        """
        The direction to be applied in the slide transition.
        """

    def blend_frames(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        # TODO: What if we receive 't' instead (?)
        # t: float
        t_progress: float
    ) -> np.ndarray:
        """
        Get the frame that is the result of applying the
        provided `t_progress` to the transition configuration.
        """
        h, w = frame_a.shape[:2]
        offset = int(w * t_progress)

        result = np.zeros_like(frame_a)
        # TODO: Handle other directions
        # TODO: Create Enum with the possibilities
        if self.direction == 'left':
            # To the left, by default
            result[:, :w-offset] = frame_a[:, offset:]
            result[:, w-offset:] = frame_b[:, :offset]

        return result
