from typing import List, Union, TYPE_CHECKING, Literal, Optional
from .video_base import VideoBase

if TYPE_CHECKING:
    from typing import Self
    from .transition import Transition

class Scene(VideoBase):
    """Scene class for managing multiple video elements as a group.

    A Scene groups multiple VideoBase elements (text, images, videos, audio) and manages
    their collective timing. Scenes can be positioned at specific times in the timeline
    and automatically handle BGM duration adjustments.

    Attributes:
        elements: List of VideoBase elements in this scene
        start_time: Start time of the scene in seconds
        duration: Total duration of the scene in seconds
        transition_in: Optional transition effect when scene starts
        transition_out: Optional transition effect when scene ends
    """

    def __init__(self) -> None:
        """Initialize a new Scene with no elements."""
        super().__init__()  # Initialize VideoBase
        self.elements: List[Union[VideoBase, 'Scene']] = []
        # Note: start_time and duration are inherited from VideoBase
        # Override the inherited start_time to maintain Scene's None-based logic
        self.start_time: float = None  # None means not explicitly set
        self.duration: float = 0.0
        self._has_content_at_start: bool = False  # Track if scene has content at time 0

        # Transition effects
        self.transition_in: Optional['Transition'] = None
        self.transition_out: Optional['Transition'] = None
        self._transition_alpha_multiplier: float = 1.0  # Current alpha multiplier from transitions
    
    def add(self, element: Union[VideoBase, 'Scene'], layer: Literal["top", "bottom"] = "top") -> 'Scene':
        """Add an element or scene to this scene.
        
        Args:
            element: VideoBase element (text, image, video, audio) or Scene to add
            layer: "top" to add on top (rendered last), "bottom" to add at bottom (rendered first)
            
        Returns:
            Self for method chaining
        """
        from .audio_element import AudioElement
        from .video_element import VideoElement
        from .image_element import ImageElement

        # Add element based on layer parameter
        if layer == "bottom":
            self.elements.insert(0, element)
        else:  # layer == "top" (default)
            self.elements.append(element)
        
        # Handle duration calculation for different element types
        if isinstance(element, Scene):
            # シーンのstart_timeが明示的に設定されていない場合（Noneの場合）、
            # 前のシーンの終了時間を開始時間として設定（逐次再生）
            if element.start_time is None:
                # 子シーンが0秒時点でコンテンツを持っているかチェック
                child_has_content_at_start = self._scene_has_content_at_time(element, 0.0)
                
                if child_has_content_at_start and not self._has_content_at_start:
                    # 子シーンに0秒時点でコンテンツがあり、親シーンにまだ0秒コンテンツがない場合
                    # 子シーンを0秒から開始させる
                    element.start_time = 0.0
                    self._has_content_at_start = True
                else:
                    # 通常の逐次配置
                    last_scene_end_time = 0.0
                    for i, existing_element in enumerate(self.elements[:-1]):  # Exclude the just-added element
                        if isinstance(existing_element, Scene):
                            existing_start = existing_element.start_time if existing_element.start_time is not None else 0.0
                            existing_end = existing_start + existing_element.duration
                            last_scene_end_time = max(last_scene_end_time, existing_end)
                    element.start_time = last_scene_end_time
            
            # For nested scenes, calculate end time based on scene's own timing
            element_start = element.start_time if element.start_time is not None else 0.0
            scene_end_time = element_start + element.duration
            old_duration = self.duration
            self.duration = max(self.duration, scene_end_time)
        else:
            # BGMモードでないオーディオ要素とループモードでないビデオ/画像要素と他の要素のみがシーン時間に影響
            is_bgm_audio = isinstance(element, AudioElement) and getattr(element, 'loop_until_scene_end', False)
            is_loop_video = isinstance(element, VideoElement) and (getattr(element, 'loop_until_scene_end', False) or getattr(element, '_wants_scene_duration', False))
            is_loop_image = isinstance(element, ImageElement) and (getattr(element, 'loop_until_scene_end', False) or getattr(element, '_wants_scene_duration', False))
            
            if not (is_bgm_audio or is_loop_video or is_loop_image):
                element_end_time = element.start_time + element.duration
                old_duration = self.duration
                self.duration = max(self.duration, element_end_time)
        
        # BGMモードのオーディオ要素とループモードのビデオ/画像要素の持続時間を更新（シーン時間決定後）
        self._update_loop_element_durations()
        return self
    
    def _scene_has_content_at_time(self, scene: 'Scene', time: float) -> bool:
        """Check if a scene has any visible content at the specified time.
        
        Args:
            scene: Scene to check
            time: Time to check (relative to scene start)
            
        Returns:
            True if scene has visible content at the specified time
        """
        for element in scene.elements:
            if isinstance(element, Scene):
                # Recursively check nested scenes
                element_start = element.start_time if element.start_time is not None else 0.0
                if element_start <= time < element_start + element.duration:
                    if self._scene_has_content_at_time(element, time - element_start):
                        return True
            else:
                # Check if non-scene element is visible at this time
                if element.start_time <= time < element.start_time + element.duration:
                    return True
        return False
    
    def _update_loop_element_durations(self) -> None:
        """Update loop element durations to match scene length.
        
        This method finds all audio, video, and image elements with loop_until_scene_end=True
        and updates their duration to match the scene's total duration.
        """
        from .audio_element import AudioElement
        from .video_element import VideoElement
        from .image_element import ImageElement
        
        for element in self.elements:
            if isinstance(element, Scene):
                # For nested scenes, recursively update their loop elements
                element._update_loop_element_durations()
            elif isinstance(element, AudioElement) and element.loop_until_scene_end:
                element.update_duration_for_scene(self.duration)
            elif isinstance(element, VideoElement) and (element.loop_until_scene_end or getattr(element, '_wants_scene_duration', False)):
                element.update_duration_for_scene(self.duration)
            elif isinstance(element, ImageElement) and (element.loop_until_scene_end or getattr(element, '_wants_scene_duration', False)):
                element.update_duration_for_scene(self.duration)
    
    def start_at(self, time: float) -> 'Scene':
        """Set the start time of this scene.

        Args:
            time: Start time in seconds

        Returns:
            Self for method chaining
        """
        self.start_time = time
        return self

    def set_transition_in(self, transition: 'Transition') -> 'Scene':
        """Set the transition effect when the scene starts (fade in).

        Args:
            transition: Transition instance to apply at scene start

        Returns:
            Self for method chaining
        """
        self.transition_in = transition
        return self

    def set_transition_out(self, transition: 'Transition') -> 'Scene':
        """Set the transition effect when the scene ends (fade out).

        Args:
            transition: Transition instance to apply at scene end

        Returns:
            Self for method chaining
        """
        self.transition_out = transition
        return self
    
    def is_visible_at(self, time: float) -> bool:
        """Check if scene is visible at the specified time.
        
        Overrides VideoBase method to handle Scene's None start_time.
        
        Args:
            time: Time in seconds to check
            
        Returns:
            True if scene is visible at the given time
        """
        start_time = self.start_time if self.start_time is not None else 0.0
        return start_time <= time < (start_time + self.duration)
    
    def calculate_size(self) -> None:
        """Calculate scene size based on contained elements.
        
        For Scene objects, size is determined by the bounding box of all contained elements.
        This is required by VideoBase interface.
        """
        # Scene size is conceptual - it contains other elements
        # For now, we'll set a default size, but this could be enhanced
        # to calculate actual bounding box of all elements
        self.width = 0
        self.height = 0
    
    def _calculate_transition_alpha(self, scene_time: float) -> float:
        """Calculate alpha multiplier based on active transitions.

        Args:
            scene_time: Time relative to scene start (0 to duration)

        Returns:
            Alpha multiplier (0.0 to 1.0)
        """
        alpha_multiplier = 1.0

        # Check for transition in (at scene start)
        if self.transition_in is not None:
            if scene_time < self.transition_in.duration:
                # We're in the transition-in period
                progress = scene_time / self.transition_in.duration
                alpha_multiplier *= self.transition_in.get_alpha_multiplier(progress, 'in')

        # Check for transition out (at scene end)
        if self.transition_out is not None:
            time_before_end = self.duration - scene_time
            if time_before_end < self.transition_out.duration:
                # We're in the transition-out period
                progress = (self.transition_out.duration - time_before_end) / self.transition_out.duration
                alpha_multiplier *= self.transition_out.get_alpha_multiplier(progress, 'out')

        return alpha_multiplier

    def _apply_transition_overlay(self, alpha: float) -> None:
        """Apply transition effect using a full-screen overlay (post-process).

        This method renders a semi-transparent black overlay on top of all scene elements
        to create a fade effect. This approach works with all element types regardless of
        how they handle OpenGL state.

        Args:
            alpha: Transition alpha (0.0 = fully black/invisible, 1.0 = fully visible)
        """
        from OpenGL.GL import glDisable, glEnable, glColor4f, glBegin, glEnd, glVertex2f, GL_TEXTURE_2D, GL_QUADS

        # Calculate fade amount (inverse of alpha)
        # alpha=0 → fade_amount=1.0 → fully black
        # alpha=1 → fade_amount=0.0 → fully transparent (no overlay)
        fade_amount = 1.0 - alpha

        # Disable textures for overlay rendering
        glDisable(GL_TEXTURE_2D)

        # Set overlay color: black with calculated alpha
        glColor4f(0.0, 0.0, 0.0, fade_amount)

        # Render full-screen quad
        # Use very large coordinates to ensure full coverage regardless of scene bounds
        glBegin(GL_QUADS)
        glVertex2f(-10000, -10000)
        glVertex2f(30000, -10000)
        glVertex2f(30000, 30000)
        glVertex2f(-10000, 30000)
        glEnd()

        # Reset color to default
        glColor4f(1.0, 1.0, 1.0, 1.0)

    def render(self, time: float) -> None:
        """Render all elements in this scene at the given time.

        This method now implements the VideoBase interface properly.

        Args:
            time: Current time in seconds (when called from VideoBase context,
                  this is scene-relative time; when called from MasterScene,
                  this needs time coordinate transformation)
        """
        # First, update animated properties as required by VideoBase
        self.update_animated_properties(time)

        # Check if the scene should be visible at this time
        if not self.is_visible_at(time):
            return

        # Calculate scene-relative time
        # For compatibility with existing behavior, we need to handle both:
        # 1. Direct calls from MasterScene (time is absolute)
        # 2. Calls from parent Scene (time is already relative)

        # If this is a top-level scene call (from MasterScene),
        # time is absolute and we need to make it relative
        start_time = self.start_time if self.start_time is not None else 0.0

        # Check if we're being called as a nested scene (time < self.duration indicates relative time)
        # or as a top-level scene (time >= start_time indicates absolute time)
        if time >= start_time and self.start_time is not None:
            # This looks like absolute time from MasterScene
            scene_time = time - start_time
        else:
            # This looks like relative time from parent scene
            scene_time = time

        # Bound check for scene duration
        if scene_time < 0 or scene_time > self.duration:
            return

        # Calculate transition alpha multiplier
        transition_alpha = self._calculate_transition_alpha(scene_time)

        # If transition makes scene completely invisible, skip rendering
        if transition_alpha <= 0.0:
            return

        # Render all elements with scene-relative time (no pre-processing)
        for element in self.elements:
            element.render(scene_time)

        # Apply transition effect as post-process overlay
        if transition_alpha < 1.0:
            self._apply_transition_overlay(transition_alpha)