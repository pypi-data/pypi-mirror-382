import os
from typing import Optional
import numpy as np
from OpenGL.GL import *
from PIL import Image
from .video_base import VideoBase


class ImageElement(VideoBase):
    """Image element for rendering image files with scaling and styling support.
    
    This class extends VideoBase to provide image rendering capabilities with support for
    various image formats, scaling, cropping, corner radius, borders, and backgrounds.
    
    Attributes:
        image_path: Path to the image file to load
        scale: Scale multiplier for the image size
        texture_id: OpenGL texture ID for the loaded image
        texture_width: Width of the OpenGL texture
        texture_height: Height of the OpenGL texture
        original_width: Original width of the source image
        original_height: Original height of the source image
    """
    
    def __init__(self, image_path: str, scale: float = 1.0) -> None:
        """Initialize a new ImageElement.
        
        Args:
            image_path: Path to the image file (supports common formats like PNG, JPG, etc.)
            scale: Scale multiplier for the image (1.0 = original size, 0.5 = half size, etc.)
        """
        super().__init__()
        self.image_path: str = image_path
        self.scale: float = scale
        self.texture_id: Optional[int] = None
        self.texture_width: int = 0
        self.texture_height: int = 0
        self.original_width: int = 0
        self.original_height: int = 0
        self.loop_until_scene_end: bool = False
        self._wants_scene_duration: bool = False
        self._create_image_texture()
        # 初期化時にサイズを計算
        self.calculate_size()
    
    def _create_image_texture(self) -> None:
        """Initialize image texture creation (deferred until OpenGL context is available).
        
        This method marks the texture as needing creation but doesn't actually create it
        until an OpenGL context is available during rendering.
        """
        # Texture creation is deferred until render time (requires OpenGL context)
        self.texture_created = False
    
    def _create_texture_now(self) -> None:
        """Create OpenGL texture for the image within an OpenGL context.
        
        This method handles image loading, format conversion, scaling, cropping,
        corner radius, border/background application, and OpenGL texture creation.
        """
        if not os.path.exists(self.image_path):
            print(f"Warning: Image file not found: {self.image_path}")
            return
        
        try:
            # Load image
            img = Image.open(self.image_path)
            
            # Convert to RGBA format (for alpha channel support)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Save original size
            self.original_width, self.original_height = img.size
            
            # Apply scaling
            if self.scale != 1.0:
                new_width = int(self.original_width * self.scale)
                new_height = int(self.original_height * self.scale)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Apply crop if specified
            img = self._apply_crop_to_image(img)
            
            # Apply corner radius clipping to image content
            img = self._apply_corner_radius_to_image(img)
            
            # Apply border and background
            img = self._apply_border_and_background_to_image(img)
            
            # Apply blur effect
            img = self._apply_blur_to_image(img)
            
            # Update texture size
            self.texture_width, self.texture_height = img.size
            
            # ボックスサイズを更新（背景・枠線を含む最終サイズ）
            self.width = self.texture_width
            self.height = self.texture_height
            
            # Convert image to NumPy array and flip vertically for OpenGL
            img_data = np.array(img)
            img_data = np.flipud(img_data)  # Flip image vertically for OpenGL coordinate system
            
            # Generate OpenGL texture
            self.texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            
            # Set texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            
            # Upload texture data
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.texture_width, self.texture_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
            
            glBindTexture(GL_TEXTURE_2D, 0)
            self.texture_created = True
            
        except Exception as e:
            print(f"Error loading image {self.image_path}: {e}")
            self.texture_created = False
    
    def set_scale(self, scale: float) -> 'ImageElement':
        """Set image scale multiplier.
        
        Args:
            scale: Scale multiplier (1.0 = original size, 0.5 = half size, 2.0 = double size)
            
        Returns:
            Self for method chaining
        """
        self.scale = scale
        # Need to recreate texture
        if self.texture_created:
            self.texture_created = False
        # サイズを再計算
        self.calculate_size()
        return self
    
    def set_loop_until_scene_end(self, loop: bool = True) -> 'ImageElement':
        """Set whether to display image until scene ends.
        
        When enabled, the image will automatically adjust its duration to match
        the parent scene's duration, staying visible for the entire scene.
        
        Args:
            loop: If True, image will be displayed until the scene ends
            
        Returns:
            Self for method chaining
        """
        self.loop_until_scene_end = loop
        
        # If enabling loop mode, mark that we want to inherit scene duration
        if loop:
            self._wants_scene_duration = True

        return self
    
    def update_duration_for_scene(self, scene_duration: float) -> None:
        """Update duration to match scene duration when in loop mode.
        
        Args:
            scene_duration: Duration of the containing scene in seconds
        """
        if self.loop_until_scene_end or self._wants_scene_duration:
            # 画像はシーンの長さに合わせて表示時間を調整
            if scene_duration > 0:  # シーンに他の要素がある場合のみ
                self.duration = scene_duration
    
    def start_at(self, start_time: float) -> 'ImageElement':
        """Set start time.
        
        Args:
            start_time: Start time in seconds
            
        Returns:
            Self for method chaining
        """
        super().start_at(start_time)
        return self
    
    def set_duration(self, duration: float) -> 'ImageElement':
        """Set duration.
        
        Args:
            duration: Duration in seconds
            
        Returns:
            Self for method chaining
        """
        super().set_duration(duration)
        return self
    
    def render(self, time: float) -> None:
        """Render the image element with OpenGL.
        
        Args:
            time: Current time in seconds for animation updates
        """
        if not self.is_visible_at(time):
            return
        
        # Create texture if not yet created
        if not self.texture_created:
            self._create_texture_now()
        
        if self.texture_id is None or not self.texture_created:
            return
        
        # Update animated properties first
        self.update_animated_properties(time)
        
        # Get animated properties
        animated_props = self.get_animated_properties(time)
        current_alpha = animated_props.get('alpha', 1.0)
        
        # Get actual render position using the fixed VideoBase method
        # This already considers scale in the anchor offset calculation
        render_x, render_y, scaled_width, scaled_height = self.get_actual_render_position()
        
        # Save current OpenGL matrix state
        glPushMatrix()
        
        # Apply transformations (rotation and scale) around the center
        center_x = render_x + scaled_width / 2
        center_y = render_y + scaled_height / 2
        
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
        
        # Move back from center
        glTranslatef(-center_x, -center_y, 0)
        
        # Apply alpha
        if current_alpha < 1.0:
            glColor4f(1.0, 1.0, 1.0, current_alpha)
        
        # Enable texture
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        # Enable alpha blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Set texture environment to modulate (applies color/alpha)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        
        # Draw textured quad with corrected texture coordinates and animation
        glBegin(GL_QUADS)
        # Bottom-left
        glTexCoord2f(0.0, 0.0)
        glVertex2f(render_x, render_y + scaled_height)
        
        # Bottom-right
        glTexCoord2f(1.0, 0.0)
        glVertex2f(render_x + scaled_width, render_y + scaled_height)
        
        # Top-right
        glTexCoord2f(1.0, 1.0)
        glVertex2f(render_x + scaled_width, render_y)
        
        # Top-left
        glTexCoord2f(0.0, 1.0)
        glVertex2f(render_x, render_y)
        glEnd()
        
        # Restore matrix state
        glPopMatrix()

    def calculate_size(self) -> None:
        """Pre-calculate image box size including scaling, cropping, padding and styling.
        
        This method reads image metadata and calculates the final box size
        including scaling, cropping, background padding and border width to set the width and height attributes.
        """
        if not os.path.exists(self.image_path):
            self.width = 0
            self.height = 0
            return
        
        try:
            # 画像の情報だけを取得（実際の読み込みはしない）
            from PIL import Image
            with Image.open(self.image_path) as img:
                original_width, original_height = img.size
            
            # スケールを適用
            scaled_width = int(original_width * self.scale)
            scaled_height = int(original_height * self.scale)
            
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
            
        except Exception as e:
            print(f"Error calculating image size {self.image_path}: {e}")
            self.width = 0
            self.height = 0
    
    def __del__(self) -> None:
        """Destructor to clean up OpenGL texture resources.
        
        Safely deletes the OpenGL texture if it was created to prevent memory leaks.
        """
        if self.texture_id:
            try:
                glDeleteTextures(1, [self.texture_id])
            except:
                pass