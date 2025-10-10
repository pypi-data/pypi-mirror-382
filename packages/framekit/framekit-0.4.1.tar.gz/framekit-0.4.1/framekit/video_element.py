import os
from typing import Optional, Tuple, Any
import cv2
import numpy as np
from OpenGL.GL import *
from PIL import Image
from .video_base import VideoBase
from .audio_element import AudioElement
from .master_scene_element import has_audio_stream


class VideoElement(VideoBase):
    """Video clip element for rendering video files with audio support.
    
    This class extends VideoBase to provide video rendering capabilities with support for
    various video formats, frame-accurate timing, scaling, cropping, borders, and automatic
    audio track integration.
    
    Attributes:
        video_path: Path to the video file to load
        scale: Scale multiplier for video size
        texture_id: OpenGL texture ID for the current frame
        texture_width: Width of the OpenGL texture
        texture_height: Height of the OpenGL texture
        original_width: Original width of the source video
        original_height: Original height of the source video
        video_capture: OpenCV VideoCapture object
        fps: Frames per second of the video
        total_frames: Total number of frames in the video
        current_frame_data: Current frame data as numpy array
        audio_element: Associated AudioElement for video soundtrack
        loop_until_scene_end: Whether to loop video until scene ends
        original_duration: Original duration of the video file
    """
    
    def __init__(self, video_path: str, scale: float = 1.0) -> None:
        """Initialize a new VideoElement.
        
        Args:
            video_path: Path to the video file (supports common formats like MP4, MOV, etc.)
            scale: Scale multiplier for the video (1.0 = original size, 0.5 = half size, etc.)
        """
        super().__init__()
        self.video_path: str = video_path
        self.scale: float = scale
        self.texture_id: Optional[int] = None
        self.texture_width: int = 0
        self.texture_height: int = 0
        self.original_width: int = 0
        self.original_height: int = 0
        self.video_capture: Optional[cv2.VideoCapture] = None
        self.fps: float = 30.0
        self.total_frames: int = 0
        self.current_frame_data: Optional[np.ndarray] = None
        self.audio_element: Optional[AudioElement] = None
        self.loop_until_scene_end: bool = False
        self.original_duration: float = 0.0
        self._wants_scene_duration: bool = False
        self._create_video_texture()
        # 初期化時にサイズを計算
        self.calculate_size()
        # オーディオ要素を作成（遅延作成）
        self.audio_element = None
        self._audio_element_created = False
    
    def _create_video_texture(self) -> None:
        """Initialize video texture creation (deferred until OpenGL context is available).
        
        This method loads video metadata and marks the texture as needing creation
        but doesn't actually create it until an OpenGL context is available during rendering.
        """
        # Texture creation is deferred until render time (requires OpenGL context)
        self.texture_created = False
        self._load_video_info()
    
    def _load_video_info(self) -> None:
        """Load video file information and properties.
        
        This method opens the video file, extracts metadata like dimensions, framerate,
        and frame count, and calculates the video duration.
        """
        if not os.path.exists(self.video_path):
            print(f"Warning: Video file not found: {self.video_path}")
            return
        
        try:
            self.video_capture = cv2.VideoCapture(self.video_path)
            
            if not self.video_capture.isOpened():
                print(f"Error: Cannot open video file: {self.video_path}")
                return
            
            # Get video properties
            self.original_width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.original_height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = self.video_capture.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calculate scaled dimensions (border/background will be applied at render time)
            base_width = int(self.original_width * self.scale)
            base_height = int(self.original_height * self.scale)
            
            # Add padding to texture dimensions
            self.texture_width = base_width + self.padding['left'] + self.padding['right']
            self.texture_height = base_height + self.padding['top'] + self.padding['bottom']
            
            # Set duration to video length
            if self.fps > 0 and self.total_frames > 0:
                video_duration = self.total_frames / self.fps
                self.duration = video_duration
                self.original_duration = video_duration

        except Exception as e:
            print(f"Error loading video info {self.video_path}: {e}")
    
    def _create_audio_element(self) -> None:
        """Create audio element from video file soundtrack.
        
        This method creates an AudioElement instance to handle the video's audio track,
        synchronizing it with the video's timing and playback settings.
        Only creates the audio element if the video file actually has an audio stream.
        """
        if self._audio_element_created:
            return
        
        # Check if the video file actually has an audio stream
        if not has_audio_stream(self.video_path):
            self.audio_element = None
            self._audio_element_created = True
            return
            
        try:
            # VideoElementと同じタイミングでオーディオを再生するようにAudioElementを作成
            self.audio_element = AudioElement(self.video_path, volume=1.0)
            # VideoElementと同じstart_timeとdurationを設定
            self._sync_audio_timing()
            self._audio_element_created = True
            print(f"Created audio element for video: {self.video_path}")
        except Exception as e:
            print(f"Failed to create audio element for {self.video_path}: {e}")
            self.audio_element = None
            self._audio_element_created = True
    
    def _sync_audio_timing(self) -> None:
        """Synchronize audio element timing with video element.
        
        Ensures that the associated audio element has the same start time and
        duration as the video element for perfect synchronization.
        """
        if self.audio_element:
            self.audio_element.start_at(self.start_time)
            self.audio_element.set_duration(self.duration)

    def get_audio_element(self) -> Optional[AudioElement]:
        """Get the associated audio element for this video.
        
        Returns:
            AudioElement instance if audio is available, None otherwise
        """
        return self.audio_element
    
    def _create_texture_now(self) -> None:
        """Create OpenGL texture for video frames.
        
        This method creates an OpenGL texture that will be updated with video frame data
        during rendering. The texture is configured for efficient frame updates.
        """
        if self.texture_id is None:
            self.texture_id = glGenTextures(1)
        
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        # Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glBindTexture(GL_TEXTURE_2D, 0)
        self.texture_created = True
    
    def _get_frame_at_time(self, video_time: float) -> Optional[np.ndarray]:
        """Get video frame at a specific time.
        
        Args:
            video_time: Time in seconds within the video to get the frame from
            
        Returns:
            Frame data as numpy array in RGBA format, or None if frame unavailable
        """
        if self.video_capture is None or not self.video_capture.isOpened():
            return None
        
        # Calculate frame number based on time
        frame_number = int(video_time * self.fps)
        frame_number = max(0, min(frame_number, self.total_frames - 1))
        
        # Set video position to desired frame
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        # Read frame
        ret, frame = self.video_capture.read()
        if not ret:
            return None
        
        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize if needed
        if self.scale != 1.0:
            new_width = int(self.original_width * self.scale)
            new_height = int(self.original_height * self.scale)
            frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        
        # Add alpha channel
        alpha = np.full((frame.shape[0], frame.shape[1], 1), 255, dtype=np.uint8)
        frame = np.concatenate([frame, alpha], axis=2)
        
        # Convert to PIL Image for crop and corner radius and border/background processing
        pil_frame = Image.fromarray(frame, 'RGBA')
        
        # Apply crop if specified
        pil_frame = self._apply_crop_to_image(pil_frame)
        
        # Apply corner radius clipping to video frame
        pil_frame = self._apply_corner_radius_to_image(pil_frame)
        
        # Apply border and background
        pil_frame = self._apply_border_and_background_to_image(pil_frame)
        
        # Apply blur effect
        pil_frame = self._apply_blur_to_image(pil_frame)
        
        # ボックスサイズを更新（背景・枠線を含む最終サイズ）
        self.width = pil_frame.size[0]
        self.height = pil_frame.size[1]
        
        # Convert back to numpy array
        frame = np.array(pil_frame)
        
        # Flip vertically for OpenGL coordinate system
        frame = np.flipud(frame)
        
        return frame
    
    def set_scale(self, scale: float) -> 'VideoElement':
        """Set video scale multiplier.
        
        Args:
            scale: Scale multiplier (1.0 = original size, 0.5 = half size, 2.0 = double size)
            
        Returns:
            Self for method chaining
        """
        self.scale = scale
        # Update texture dimensions (border/background will be applied at render time)
        if hasattr(self, 'original_width'):
            base_width = int(self.original_width * self.scale)
            base_height = int(self.original_height * self.scale)
            
            # Add padding to texture dimensions
            self.texture_width = base_width + self.padding['left'] + self.padding['right']
            self.texture_height = base_height + self.padding['top'] + self.padding['bottom']
            
            # ボックスサイズも更新（推定値、実際は描画時に正確な値が設定される）
            border_size = self.border_width * 2 if self.border_color else 0
            self.width = self.texture_width + border_size
            self.height = self.texture_height + border_size
        return self
    
    def start_at(self, start_time: float) -> 'VideoElement':
        """Set start time and synchronize with audio element.
        
        Args:
            start_time: Start time in seconds
            
        Returns:
            Self for method chaining
        """
        super().start_at(start_time)
        self._ensure_audio_element()
        self._sync_audio_timing()
        return self
    
    def set_duration(self, duration: float) -> 'VideoElement':
        """Set duration and synchronize with audio element.
        
        Args:
            duration: Duration in seconds
            
        Returns:
            Self for method chaining
        """
        super().set_duration(duration)
        self._ensure_audio_element()
        self._sync_audio_timing()
        return self
    
    def _ensure_audio_element(self) -> None:
        """Ensure audio element is created before using it.
        
        Creates the audio element if it hasn't been created yet. This is used
        to lazily initialize audio support when audio-related methods are called.
        """
        if not self._audio_element_created:
            self._create_audio_element()
    
    def set_volume(self, volume: float) -> 'VideoElement':
        """Set audio volume level.
        
        Args:
            volume: Volume level (0.0 = muted, 1.0 = full volume, >1.0 = amplified)
            
        Returns:
            Self for method chaining
        """
        self._ensure_audio_element()
        if self.audio_element:
            self.audio_element.set_volume(volume)
        return self
    
    def set_audio_fade_in(self, duration: float) -> 'VideoElement':
        """Set audio fade-in duration.
        
        Args:
            duration: Fade-in duration in seconds
            
        Returns:
            Self for method chaining
        """
        self._ensure_audio_element()
        if self.audio_element:
            self.audio_element.set_fade_in(duration)
        return self
    
    def set_audio_fade_out(self, duration: float) -> 'VideoElement':
        """Set audio fade-out duration.
        
        Args:
            duration: Fade-out duration in seconds
            
        Returns:
            Self for method chaining
        """
        self._ensure_audio_element()
        if self.audio_element:
            self.audio_element.set_fade_out(duration)
        return self
    
    def mute_audio(self) -> 'VideoElement':
        """Mute video audio track.
        
        Returns:
            Self for method chaining
        """
        self._ensure_audio_element()
        if self.audio_element:
            self.audio_element.mute()
        return self
    
    def unmute_audio(self) -> 'VideoElement':
        """Unmute video audio track.
        
        Returns:
            Self for method chaining
        """
        self._ensure_audio_element()
        if self.audio_element:
            self.audio_element.unmute()
        return self
    
    def get_audio_volume(self) -> float:
        """Get current audio volume level.
        
        Returns:
            Current volume level (0.0 = muted, 1.0 = full volume)
        """
        self._ensure_audio_element()
        if self.audio_element:
            return self.audio_element.volume
        return 0.0
    
    def set_loop_until_scene_end(self, loop: bool = True) -> 'VideoElement':
        """Set whether to loop video until scene ends.
        
        When enabled, the video will automatically adjust its duration to match
        the parent scene's duration, either by looping (if scene is longer than video)
        or cutting (if scene is shorter than video).
        
        Args:
            loop: If True, video will loop continuously until the scene ends
            
        Returns:
            Self for method chaining
        """
        self.loop_until_scene_end = loop
        
        # If enabling loop mode and no explicit duration is set, 
        # we'll let the scene determine our duration
        if loop and hasattr(self, 'original_duration') and self.original_duration > 0:
            # Mark that we want to inherit scene duration
            self._wants_scene_duration = True

        return self
    
    def update_duration_for_scene(self, scene_duration: float) -> None:
        """Update duration to match scene duration when in loop mode.
        
        Args:
            scene_duration: Duration of the containing scene in seconds
        """
        if self.loop_until_scene_end or self._wants_scene_duration:
            # ビデオはシーンの長さに合わせて調整（ループまたは強制終了）
            if scene_duration > 0:  # シーンに他の要素がある場合のみ
                self.duration = scene_duration
                
                # オーディオ要素も同期
                self._ensure_audio_element()
                if self.audio_element and hasattr(self.audio_element, 'update_duration_for_scene'):
                    self.audio_element.update_duration_for_scene(scene_duration)
    
    def render(self, time: float) -> None:
        """Render video frame at the current time.
        
        Args:
            time: Current time in seconds for frame selection and animation updates
        """
        if not self.is_visible_at(time):
            return
        
        if self.video_capture is None:
            return
        
        # Create texture if not yet created
        if not self.texture_created:
            self._create_texture_now()
        
        if self.texture_id is None:
            return
        
        # Calculate video time (time within the video clip)
        video_time = time - self.start_time
        
        # Handle looping or cutting when scene duration adjustment is enabled
        if self.loop_until_scene_end or self._wants_scene_duration:
            if self.original_duration > 0:
                if video_time >= self.original_duration:
                    # Loop the video by taking modulo of the original duration
                    video_time = video_time % self.original_duration
                elif video_time < 0:
                    # Handle negative time (shouldn't normally happen, but safety check)
                    video_time = 0
                # If video_time is within original duration, use it as-is (handles cutting case)
        
        # Get current frame
        frame_data = self._get_frame_at_time(video_time)
        if frame_data is None:
            return
        
        # Save current OpenGL state
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        
        # Update texture with current frame
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        # Upload frame data to texture (frame_data already includes border/background)
        actual_height, actual_width = frame_data.shape[:2]
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, actual_width, actual_height, 
                     0, GL_RGBA, GL_UNSIGNED_BYTE, frame_data)
        
        # Update texture dimensions with actual frame size
        self.texture_width = actual_width
        self.texture_height = actual_height
        
        # Get animated properties for transformation
        animated_props = self.get_animated_properties(time)
        
        # Get actual render position using anchor calculation
        # Temporarily set the current size for anchor calculation
        original_width, original_height = self.width, self.height
        self.width, self.height = actual_width, actual_height
        
        render_x, render_y, _, _ = self.get_actual_render_position()
        
        # Apply animation offsets
        if 'x' in animated_props:
            render_x = animated_props['x'] + self._calculate_anchor_offset(actual_width, actual_height)[0]
        if 'y' in animated_props:
            render_y = animated_props['y'] + self._calculate_anchor_offset(actual_width, actual_height)[1]
        
        # Restore original size
        self.width, self.height = original_width, original_height
        
        # Save current OpenGL matrix state
        glPushMatrix()
        
        # Apply transformations (rotation and scale) around the center
        center_x = render_x + self.texture_width / 2
        center_y = render_y + self.texture_height / 2
        
        # Move to center for rotation
        glTranslatef(center_x, center_y, 0)
        
        # Apply rotation if set
        current_rotation = animated_props.get('rotation', getattr(self, 'rotation', 0.0))
        if current_rotation != 0:
            glRotatef(current_rotation, 0, 0, 1)
        
        # Apply flip transformations
        flip_x = -1.0 if getattr(self, 'flip_horizontal', False) else 1.0
        flip_y = -1.0 if getattr(self, 'flip_vertical', False) else 1.0
        if flip_x != 1.0 or flip_y != 1.0:
            glScalef(flip_x, flip_y, 1.0)
        
        # Apply scale if set
        current_scale = animated_props.get('scale', getattr(self, 'scale', 1.0))
        if current_scale != 1.0:
            glScalef(current_scale, current_scale, 1.0)
        
        # Move back from center
        glTranslatef(-center_x, -center_y, 0)
        
        # Apply alpha
        current_alpha = animated_props.get('alpha', 1.0)
        if current_alpha < 1.0:
            glColor4f(1.0, 1.0, 1.0, current_alpha / 255.0)
        
        # Enable alpha blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Set texture environment to replace (preserves texture colors)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        
        # Draw textured quad with corrected texture coordinates
        glBegin(GL_QUADS)
        # Bottom-left
        glTexCoord2f(0.0, 0.0)
        glVertex2f(render_x, render_y + self.texture_height)
        
        # Bottom-right
        glTexCoord2f(1.0, 0.0)
        glVertex2f(render_x + self.texture_width, render_y + self.texture_height)
        
        # Top-right
        glTexCoord2f(1.0, 1.0)
        glVertex2f(render_x + self.texture_width, render_y)
        
        # Top-left
        glTexCoord2f(0.0, 1.0)
        glVertex2f(render_x, render_y)
        glEnd()
        
        # Restore matrix state
        glPopMatrix()

    def calculate_size(self) -> None:
        """Pre-calculate video box size including scaling, cropping, padding and styling.
        
        This method calculates the final box size based on video dimensions, scaling,
        cropping, background padding and border width to set the width and height attributes.
        """
        if not hasattr(self, 'original_width') or self.original_width == 0:
            self.width = 0
            self.height = 0
            return
        
        # スケールを適用
        scaled_width = int(self.original_width * self.scale)
        scaled_height = int(self.original_height * self.scale)
        
        # クロップが設定されている場合はクロップサイズを使用
        if self.crop_width is not None and self.crop_height is not None:
            content_width = self.crop_width
            content_height = self.crop_height
        else:
            content_width = scaled_width
            content_height = scaled_height
        
        # パディングを含むキャンバスサイズを計算
        canvas_width = content_width + self.padding['left'] + self.padding['right']
        canvas_height = content_height + self.padding['top'] + self.padding['bottom']
        
        # 最小サイズを保証
        canvas_width = max(canvas_width, 1)
        canvas_height = max(canvas_height, 1)
        
        # ボックスサイズを更新
        self.width = canvas_width
        self.height = canvas_height
    
    def __del__(self) -> None:
        """Destructor to clean up video and OpenGL texture resources.
        
        Releases the OpenCV VideoCapture object and safely deletes the OpenGL texture
        if they were created to prevent memory leaks.
        """
        if self.video_capture:
            self.video_capture.release()
        
        if self.texture_id:
            try:
                glDeleteTextures(1, [self.texture_id])
            except:
                pass