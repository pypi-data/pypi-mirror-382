from typing import Optional, Literal
from abc import ABC, abstractmethod


class Transition(ABC):
    """Abstract base class for scene transitions.

    Transitions control how a scene appears (transition in) or disappears (transition out).
    All transition implementations should inherit from this class.

    Attributes:
        duration: Duration of the transition in seconds
    """

    def __init__(self, duration: float = 1.0) -> None:
        """Initialize a new Transition.

        Args:
            duration: Transition duration in seconds
        """
        self.duration: float = duration

    @abstractmethod
    def get_alpha_multiplier(self, progress: float, direction: Literal['in', 'out']) -> float:
        """Calculate alpha multiplier based on transition progress.

        Args:
            progress: Transition progress (0.0 to 1.0)
            direction: Transition direction ('in' for fade in, 'out' for fade out)

        Returns:
            Alpha multiplier value between 0.0 and 1.0
        """
        pass

    def get_transform(self, progress: float, direction: Literal['in', 'out']) -> dict:
        """Get additional transform properties for the transition.

        Override this method if the transition needs to modify properties
        beyond alpha (e.g., position, scale, rotation).

        Args:
            progress: Transition progress (0.0 to 1.0)
            direction: Transition direction ('in' or 'out')

        Returns:
            Dictionary of property names and values to apply
        """
        return {}


class FadeTransition(Transition):
    """Fade transition - smooth opacity change.

    Fade In: Scene gradually becomes visible (alpha: 0 → 1)
    Fade Out: Scene gradually becomes invisible (alpha: 1 → 0)

    This is the most common and versatile transition type.
    """

    def __init__(self, duration: float = 1.0, easing: Literal['linear', 'ease_in', 'ease_out', 'ease_in_out'] = 'linear') -> None:
        """Initialize a fade transition.

        Args:
            duration: Transition duration in seconds
            easing: Easing function to use ('linear', 'ease_in', 'ease_out', 'ease_in_out')
        """
        super().__init__(duration)
        self.easing = easing

    def get_alpha_multiplier(self, progress: float, direction: Literal['in', 'out']) -> float:
        """Calculate alpha multiplier for fade transition.

        Args:
            progress: Transition progress (0.0 to 1.0)
            direction: 'in' for fade in (0→1), 'out' for fade out (1→0)

        Returns:
            Alpha multiplier value between 0.0 and 1.0
        """
        # Apply easing
        eased_progress = self._apply_easing(progress)

        if direction == 'in':
            # Fade in: alpha goes from 0 to 1
            return eased_progress
        else:  # direction == 'out'
            # Fade out: alpha goes from 1 to 0
            return 1.0 - eased_progress

    def _apply_easing(self, t: float) -> float:
        """Apply easing function to progress value.

        Args:
            t: Progress value (0.0 to 1.0)

        Returns:
            Eased progress value (0.0 to 1.0)
        """
        if self.easing == 'ease_in':
            # Quadratic ease in
            return t * t
        elif self.easing == 'ease_out':
            # Quadratic ease out
            return 1 - (1 - t) * (1 - t)
        elif self.easing == 'ease_in_out':
            # Quadratic ease in-out
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        else:  # linear
            return t
