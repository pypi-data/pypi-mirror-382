from typing import Dict, Optional, Tuple, Any, Literal, Union, TypeVar
from PIL import Image, ImageDraw, ImageFilter
from .animation import Animation, AnimationManager, RepeatingAnimation

# TypeVar for method chaining with inheritance
VideoBaseT = TypeVar('VideoBaseT', bound='VideoBase')


class VideoBase:
    """Base class for all video elements.
    
    This class provides common functionality for positioning, timing, visual effects,
    animations, and rendering for all video elements like text, images, and videos.
    
    Attributes:
        x: X coordinate position
        y: Y coordinate position
        start_time: Start time in seconds
        duration: Duration in seconds
        visible: Whether the element is visible
        position_anchor: Position anchor point
        background_color: Background color as RGB tuple
        background_alpha: Background opacity (0-255)
        padding: Padding around content
        border_color: Border color as RGB tuple
        border_width: Border width in pixels
        corner_radius: Corner radius for rounded corners
        blur_strength: Blur strength (0 = no blur, higher values = more blur)
        crop_width: Crop width in pixels
        crop_height: Crop height in pixels
        crop_mode: Crop mode ('fill' or 'fit')
        width: Element width including padding and border
        height: Element height including padding and border
        texture_created: Flag indicating if texture needs recreation
        animation_manager: Manages all animations for this element
        base_x: Base X position before animations
        base_y: Base Y position before animations
        base_alpha: Base alpha value before animations
        base_scale: Base scale value before animations
        rotation: Rotation angle in degrees
        scale: Scale multiplier
    """
    
    def __init__(self) -> None:
        """Initialize a new VideoBase element with default properties."""
        self.x: float = 0.0
        self.y: float = 0.0
        self.start_time: float = 0.0
        self.duration: float = 1.0
        self.visible: bool = True
        
        # Position anchor settings
        self.position_anchor: Literal['center', 'top-left', 'top-right', 'bottom-left', 'bottom-right'] = 'top-left'
        
        # Background box settings
        self.background_color: Optional[Tuple[int, int, int]] = None
        self.background_alpha: int = 255
        self.padding: Dict[str, int] = {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}
        
        # Border settings
        self.border_color: Optional[Tuple[int, int, int]] = None
        self.border_width: int = 0
        
        # Corner radius settings
        self.corner_radius: float = 0
        
        # Blur settings
        self.blur_strength: float = 0
        
        # Crop settings
        self.crop_width: Optional[int] = None
        self.crop_height: Optional[int] = None
        self.crop_mode: Literal['fill', 'fit'] = 'fill'
        
        # Box size (final size including background and border)
        self.width: int = 0
        self.height: int = 0
        
        # Texture recreation flag
        self.texture_created: bool = False
        
        # Animation related
        self.animation_manager: AnimationManager = AnimationManager()
        self.base_x: float = 0.0  # Base position before animations
        self.base_y: float = 0.0
        self.base_alpha: int = 255  # Base alpha before animations
        self.base_scale: float = 1.0  # Base scale before animations
        self.rotation: float = 0.0  # Rotation angle in degrees
        self.scale: float = 1.0  # Scale value
        self.flip_horizontal: bool = False  # Horizontal flip flag
        self.flip_vertical: bool = False  # Vertical flip flag
    
    def position(self: VideoBaseT, x: float, y: float, anchor: Optional[Literal['center', 'top-left', 'top-right', 'bottom-left', 'bottom-right']] = None) -> VideoBaseT:
        """Set position coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            anchor: Position anchor point ('center', 'top-left', 'top-right', 'bottom-left', 'bottom-right')
                   If None, maintains current anchor setting
                   
        Returns:
            Self for method chaining
        """
        if anchor is not None:
            self.position_anchor = anchor
        
        self.x = x
        self.y = y
        self.base_x = x  # アニメーション用の基本位置も更新
        self.base_y = y
        return self
    
    def _calculate_anchor_offset(self, element_width: float, element_height: float) -> Tuple[float, float]:
        """アンカーに基づく位置オフセットを計算
        
        Args:
            element_width: 要素の幅
            element_height: 要素の高さ
            
        Returns:
            (offset_x, offset_y): アンカーに基づくオフセット
        """
        if self.position_anchor == 'center':
            return -element_width / 2, -element_height / 2
        elif self.position_anchor == 'top-right':
            return -element_width, 0
        elif self.position_anchor == 'bottom-left':
            return 0, -element_height
        elif self.position_anchor == 'bottom-right':
            return -element_width, -element_height
        else:  # 'top-left' (default)
            return 0, 0
    
    def get_actual_render_position(self) -> Tuple[float, float, float, float]:
        """Get actual rendering position and size considering scale and other factors.
        
        Returns:
            Tuple of (actual_x, actual_y, scaled_width, scaled_height)
        """
        element_width = getattr(self, 'width', 0)
        element_height = getattr(self, 'height', 0)
        
        # スケールを適用した実際のサイズを計算
        scaled_width = element_width * self.scale
        scaled_height = element_height * self.scale
        
        # スケール適用後のサイズでアンカーに基づく位置オフセットを計算
        offset_x, offset_y = self._calculate_anchor_offset(scaled_width, scaled_height)
        
        # 実際の描画位置を計算
        actual_x = self.x + offset_x
        actual_y = self.y + offset_y
        
        return actual_x, actual_y, scaled_width, scaled_height
    
    def set_duration(self: VideoBaseT, duration: float) -> VideoBaseT:
        """Set display duration in seconds.
        
        Args:
            duration: Duration in seconds
            
        Returns:
            Self for method chaining
        """
        self.duration = duration
        return self
    
    def start_at(self: VideoBaseT, time: float) -> VideoBaseT:
        """Set start time in seconds.
        
        Args:
            time: Start time in seconds
            
        Returns:
            Self for method chaining
        """
        self.start_time = time
        return self
    
    def is_visible_at(self, time: float) -> bool:
        """Check if element is visible at the specified time.
        
        Args:
            time: Time in seconds to check
            
        Returns:
            True if element is visible at the given time
        """
        return self.start_time <= time < (self.start_time + self.duration)
    
    def set_background(self: VideoBaseT, color: Tuple[int, int, int], alpha: int = 255, padding: Union[int, Dict[str, int]] = 5) -> VideoBaseT:
        """Set background color and padding.
        
        Args:
            color: RGB color tuple (0-255 for each component)
            alpha: Background opacity (0-255, where 255 is opaque)
            padding: Padding around content. Can be a single int for uniform padding
                    or a dict with keys 'top', 'right', 'bottom', 'left'
                    
        Returns:
            Self for method chaining
        """
        self.background_color = color
        self.background_alpha = alpha
        if isinstance(padding, int):
            self.padding = {'top': padding, 'right': padding, 'bottom': padding, 'left': padding}
        elif isinstance(padding, dict):
            self.padding.update(padding)
        # テクスチャを再作成する必要がある
        self.texture_created = False
        # サイズを再計算
        self.calculate_size()
        return self
    
    def set_border(self: VideoBaseT, color: Tuple[int, int, int], width: int = 1) -> VideoBaseT:
        """Set border color and width.
        
        Args:
            color: RGB color tuple (0-255 for each component)
            width: Border width in pixels
            
        Returns:
            Self for method chaining
        """
        self.border_color = color
        self.border_width = width
        # テクスチャを再作成する必要がある
        self.texture_created = False
        # サイズを再計算
        self.calculate_size()
        return self
    
    def set_corner_radius(self: VideoBaseT, radius: float) -> VideoBaseT:
        """Set corner radius for rounded corners.
        
        Args:
            radius: Corner radius in pixels (negative values are clamped to 0)
            
        Returns:
            Self for method chaining
        """
        self.corner_radius = max(0, radius)  # 負の値は0に補正
        # テクスチャを再作成する必要がある
        self.texture_created = False
        # サイズを再計算（角丸は通常サイズに影響しないが、将来の拡張のため）
        self.calculate_size()
        return self
    
    def set_crop(self: VideoBaseT, width: int, height: int, mode: Literal['fill', 'fit'] = 'fill') -> VideoBaseT:
        """Set crop size and mode.
        
        Args:
            width: Target width after cropping
            height: Target height after cropping
            mode: Crop mode - 'fill' crops overflow to fit exactly, 'fit' scales to fit within bounds
            
        Returns:
            Self for method chaining
        """
        self.crop_width = width
        self.crop_height = height
        self.crop_mode = mode
        # テクスチャを再作成する必要がある
        self.texture_created = False
        # サイズを再計算
        self.calculate_size()
        return self
    
    def set_blur(self: VideoBaseT, strength: float) -> VideoBaseT:
        """Set blur strength.
        
        Args:
            strength: Blur strength (0 = no blur, higher values = more blur)
            
        Returns:
            Self for method chaining
        """
        self.blur_strength = max(0, strength)  # 負の値は0に補正
        # テクスチャを再作成する必要がある
        self.texture_created = False
        return self
    
    def set_rotate(self: VideoBaseT, angle: float) -> VideoBaseT:
        """Set rotation angle in degrees.
        
        Args:
            angle: Rotation angle in degrees
            
        Returns:
            Self for method chaining
        """
        self.rotation = angle
        return self
    
    def set_flip(self: VideoBaseT, direction: Union[str, Literal['horizontal', 'vertical', 'both', 'none']] = 'horizontal') -> VideoBaseT:
        """Set flip options for the element.
        
        Args:
            direction: Flip direction - 'horizontal' (left-right), 'vertical' (up-down), 'both', or 'none'
            
        Returns:
            Self for method chaining
        """
        if direction == 'horizontal':
            self.flip_horizontal = True
            self.flip_vertical = False
        elif direction == 'vertical':
            self.flip_horizontal = False
            self.flip_vertical = True
        elif direction == 'both':
            self.flip_horizontal = True
            self.flip_vertical = True
        elif direction == 'none':
            self.flip_horizontal = False
            self.flip_vertical = False
        else:
            raise ValueError(f"Invalid flip direction: {direction}. Use 'horizontal', 'vertical', 'both', or 'none'")
        
        return self

    def _apply_border_and_background_to_image(self, img: Image.Image) -> Image.Image:
        """Apply background and border to an image.
        
        Args:
            img: Source image to apply effects to
            
        Returns:
            New image with background and border applied
        """
        # 元の画像サイズを取得
        original_width, original_height = img.size
        
        # パディングを含むキャンバスサイズを計算
        canvas_width = original_width + self.padding['left'] + self.padding['right']
        canvas_height = original_height + self.padding['top'] + self.padding['bottom']
        
        # 最小サイズを保証
        canvas_width = max(canvas_width, 1)
        canvas_height = max(canvas_height, 1)
        
        # キャンバス用の画像を作成
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        canvas = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
        
        # 背景ボックスを描画
        if self.background_color is not None:
            draw = ImageDraw.Draw(canvas)
            bg_color = (*self.background_color, self.background_alpha)
            
            if self.corner_radius > 0:
                # 角丸背景を描画
                draw.rounded_rectangle([0, 0, canvas_width-1, canvas_height-1], 
                                     radius=self.corner_radius, fill=bg_color)
            else:
                # 通常の四角形背景を描画
                draw.rectangle([0, 0, canvas_width-1, canvas_height-1], fill=bg_color)
        
        # 元の画像をパディング位置に合成
        canvas.paste(img, (self.padding['left'], self.padding['top']), img)
        
        # 枠線を描画
        if self.border_color is not None and self.border_width > 0:
            draw = ImageDraw.Draw(canvas)
            border_color = (*self.border_color, 255)
            
            if self.corner_radius > 0:
                # 角丸枠線を描画
                for i in range(self.border_width):
                    # 内側に向かって角丸半径を調整
                    current_radius = max(0, self.corner_radius - i)
                    draw.rounded_rectangle([i, i, canvas_width-1-i, canvas_height-1-i], 
                                         radius=current_radius, outline=border_color, width=1)
            else:
                # 通常の四角形枠線を描画
                for i in range(self.border_width):
                    draw.rectangle([i, i, canvas_width-1-i, canvas_height-1-i], 
                                 outline=border_color, width=1)
        
        return canvas
    
    def _apply_corner_radius_to_image(self, img: Image.Image) -> Image.Image:
        """Apply corner radius clipping to image content.
        
        Args:
            img: Source image to apply corner radius to
            
        Returns:
            New image with corner radius clipping applied
        """
        if self.corner_radius <= 0:
            return img
        
        # 画像サイズを取得
        width, height = img.size
        
        # 角丸半径がサイズより大きい場合は調整
        radius = min(self.corner_radius, width // 2, height // 2)
        
        # 角丸マスクを作成
        mask = Image.new('L', (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, width, height], radius=radius, fill=255)
        
        # RGBAモードに変換
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # マスクを適用して角丸にクリッピング
        img.putalpha(mask)
        
        return img
    
    def _apply_blur_to_image(self, img: Image.Image) -> Image.Image:
        """Apply blur effect to an image.
        
        Args:
            img: Source image to apply blur to
            
        Returns:
            Blurred image
        """
        if self.blur_strength <= 0:
            return img
        
        # PILのGaussianBlurフィルターを適用
        return img.filter(ImageFilter.GaussianBlur(radius=self.blur_strength))
    
    def _calculate_crop_dimensions(self, original_width: int, original_height: int) -> Tuple[int, int, int, int]:
        """Calculate crop scale and position.
        
        Args:
            original_width: Original image width
            original_height: Original image height
        
        Returns:
            Tuple of (scaled_width, scaled_height, crop_x, crop_y)
        """
        if self.crop_width is None or self.crop_height is None:
            return original_width, original_height, 0, 0
        
        target_width = self.crop_width
        target_height = self.crop_height
        
        if self.crop_mode == 'fill':
            # アスペクト比を維持して、指定サイズを完全に埋める（はみ出し部分をクロップ）
            scale = max(target_width / original_width, target_height / original_height)
        else:  # fit
            # アスペクト比を維持して、指定サイズに収まる最大サイズ
            scale = min(target_width / original_width, target_height / original_height)
        
        # スケール後のサイズ
        scaled_width = int(original_width * scale)
        scaled_height = int(original_height * scale)
        
        # クロップ位置を計算（中央クロップ）
        crop_x = max(0, (scaled_width - target_width) // 2)
        crop_y = max(0, (scaled_height - target_height) // 2)
        
        return scaled_width, scaled_height, crop_x, crop_y
    
    def _apply_crop_to_image(self, img: Image.Image) -> Image.Image:
        """Apply cropping to an image.
        
        Args:
            img: Source image to crop
            
        Returns:
            Cropped image
        """
        if self.crop_width is None or self.crop_height is None:
            return img
        
        original_width, original_height = img.size
        scaled_width, scaled_height, crop_x, crop_y = self._calculate_crop_dimensions(original_width, original_height)
        
        # まずスケールを適用
        if scaled_width != original_width or scaled_height != original_height:
            img = img.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
        
        # クロップを適用
        if self.crop_mode == 'fill':
            # fillモード: 指定サイズでクロップ
            crop_box = (crop_x, crop_y, crop_x + self.crop_width, crop_y + self.crop_height)
            img = img.crop(crop_box)
        else:  # fit
            # fitモード: 新しいキャンバスを作成して中央に配置
            canvas = Image.new('RGBA', (self.crop_width, self.crop_height), (0, 0, 0, 0))
            paste_x = (self.crop_width - scaled_width) // 2
            paste_y = (self.crop_height - scaled_height) // 2
            canvas.paste(img, (paste_x, paste_y), img)
            img = canvas
        
        return img

    def animate(self: VideoBaseT, property_name: str, animation: Animation) -> VideoBaseT:
        """Add animation to a property.
        
        Args:
            property_name: Name of the property to animate
            animation: Animation instance to apply
            
        Returns:
            Self for method chaining
        """
        # アニメーションの開始時刻を要素の開始時刻に対して相対的に設定
        animation.start_time += self.start_time
        self.animation_manager.add_animation(property_name, animation)
        return self
    
    def animate_position(self: VideoBaseT, animation: Animation, axis: Literal['x', 'y', 'both'] = 'both') -> VideoBaseT:
        """Add position animation (convenience method).
        
        Args:
            animation: Animation to apply
            axis: Axis to animate ('x', 'y', or 'both')
            
        Returns:
            Self for method chaining
        """
        if axis in ['x', 'both']:
            self.animate('x', animation)
        if axis in ['y', 'both']:
            self.animate('y', animation) 
        return self
    
    def animate_fade(self: VideoBaseT, animation: Animation) -> VideoBaseT:
        """Add fade (alpha) animation (convenience method).
        
        Args:
            animation: Animation to apply to alpha channel
            
        Returns:
            Self for method chaining
        """
        self.animate('alpha', animation)
        return self
    
    def animate_scale(self: VideoBaseT, animation: Animation) -> VideoBaseT:
        """Add scale animation (convenience method).
        
        Args:
            animation: Animation to apply to scale
            
        Returns:
            Self for method chaining
        """
        self.animate('scale', animation)
        return self
    
    def animate_rotation(self: VideoBaseT, animation: Animation) -> VideoBaseT:
        """Add rotation animation (convenience method).
        
        Args:
            animation: Animation to apply to rotation
            
        Returns:
            Self for method chaining
        """
        self.animate('rotation', animation)
        return self
    
    def animate_repeating(self: VideoBaseT, property_name: str, animation: Animation, 
                         repeat_count: int = -1, repeat_delay: float = 0.0, 
                         repeat_mode: Literal['restart', 'reverse', 'continue'] = 'restart') -> VideoBaseT:
        """Add repeating animation to a property.
        
        Args:
            property_name: Name of property to animate
            animation: Base animation to repeat
            repeat_count: Number of repetitions (-1 for infinite)
            repeat_delay: Delay between repetitions in seconds
            repeat_mode: Repeat mode ('restart', 'reverse', or 'continue')
            
        Returns:
            Self for method chaining
        """
        repeating_animation = RepeatingAnimation(
            base_animation=animation,
            repeat_count=repeat_count,
            repeat_delay=repeat_delay,
            repeat_mode=repeat_mode
        )
        repeating_animation.start_time += self.start_time
        self.animation_manager.add_animation(property_name, repeating_animation)
        return self
    
    def animate_until_scene_end(self: VideoBaseT, property_name: str, animation: Animation, 
                               repeat_delay: float = 0.0, repeat_mode: Literal['restart', 'reverse', 'continue'] = 'restart',
                               scene_duration: Optional[float] = None) -> VideoBaseT:
        """Add animation that repeats until scene end.
        
        Args:
            property_name: Name of property to animate
            animation: Base animation to repeat
            repeat_delay: Delay between repetitions in seconds
            repeat_mode: Repeat mode ('restart', 'reverse', or 'continue')
            scene_duration: Scene duration in seconds (None for auto-detection)
            
        Returns:
            Self for method chaining
        """
        # シーン継続時間を推定（実際の実装では親シーンから取得すべき）
        if scene_duration is None:
            scene_duration = self.duration  # 暫定的に要素の継続時間を使用
        
        repeating_animation = RepeatingAnimation(
            base_animation=animation,
            repeat_count=-1,
            repeat_delay=repeat_delay,
            repeat_mode=repeat_mode,
            until_scene_end=True,
            scene_duration=scene_duration
        )
        repeating_animation.start_time += self.start_time
        self.animation_manager.add_animation(property_name, repeating_animation)
        return self
    
    # Convenience methods for repeating animations
    def animate_repeating_scale(self: VideoBaseT, animation: Animation, repeat_count: int = -1, 
                               repeat_delay: float = 0.0, repeat_mode: Literal['restart', 'reverse', 'continue'] = 'restart') -> VideoBaseT:
        """Add repeating scale animation (convenience method).
        
        Args:
            animation: Animation to repeat
            repeat_count: Number of repetitions (-1 for infinite)
            repeat_delay: Delay between repetitions in seconds
            repeat_mode: Repeat mode ('restart', 'reverse', or 'continue')
            
        Returns:
            Self for method chaining
        """
        return self.animate_repeating('scale', animation, repeat_count, repeat_delay, repeat_mode)
    
    def animate_repeating_position(self: VideoBaseT, animation: Animation, axis: Literal['x', 'y', 'both'] = 'both',
                                  repeat_count: int = -1, repeat_delay: float = 0.0, 
                                  repeat_mode: Literal['restart', 'reverse', 'continue'] = 'restart') -> VideoBaseT:
        """Add repeating position animation (convenience method).
        
        Args:
            animation: Animation to repeat
            axis: Axis to animate ('x', 'y', or 'both')
            repeat_count: Number of repetitions (-1 for infinite)
            repeat_delay: Delay between repetitions in seconds
            repeat_mode: Repeat mode ('restart', 'reverse', or 'continue')
            
        Returns:
            Self for method chaining
        """
        if axis in ['x', 'both']:
            self.animate_repeating('x', animation, repeat_count, repeat_delay, repeat_mode)
        if axis in ['y', 'both']:
            self.animate_repeating('y', animation, repeat_count, repeat_delay, repeat_mode)
        return self
    
    def animate_repeating_rotation(self: VideoBaseT, animation: Animation, repeat_count: int = -1,
                                  repeat_delay: float = 0.0, repeat_mode: Literal['restart', 'reverse', 'continue'] = 'restart') -> VideoBaseT:
        """Add repeating rotation animation (convenience method).
        
        Args:
            animation: Animation to repeat
            repeat_count: Number of repetitions (-1 for infinite)
            repeat_delay: Delay between repetitions in seconds
            repeat_mode: Repeat mode ('restart', 'reverse', or 'continue')
            
        Returns:
            Self for method chaining
        """
        return self.animate_repeating('rotation', animation, repeat_count, repeat_delay, repeat_mode)
    
    def animate_pulse_until_end(self: VideoBaseT, from_scale: float = 1.0, to_scale: float = 1.2,
                               duration: float = 1.0, repeat_delay: float = 0.0,
                               scene_duration: Optional[float] = None) -> VideoBaseT:
        """Add pulse (heartbeat-like) animation until scene end (convenience method).
        
        Args:
            from_scale: Starting scale value
            to_scale: Peak scale value
            duration: Duration of one pulse cycle in seconds
            repeat_delay: Delay between pulses in seconds
            scene_duration: Scene duration (None for auto-detection)
            
        Returns:
            Self for method chaining
        """
        from animation import AnimationPresets
        pulse_animation = AnimationPresets.pulse(from_scale, to_scale, duration)
        return self.animate_until_scene_end('scale', pulse_animation, repeat_delay, 
                                          'restart', scene_duration)
    
    def animate_breathing_until_end(self: VideoBaseT, from_scale: float = 1.0, to_scale: float = 1.1,
                                   duration: float = 3.0, repeat_delay: float = 0.0,
                                   scene_duration: Optional[float] = None) -> VideoBaseT:
        """Add breathing-like scaling animation until scene end (convenience method).
        
        Args:
            from_scale: Starting scale value
            to_scale: Peak scale value
            duration: Duration of one breathing cycle in seconds
            repeat_delay: Delay between breathing cycles in seconds
            scene_duration: Scene duration (None for auto-detection)
            
        Returns:
            Self for method chaining
        """
        from animation import AnimationPresets
        breathing_animation = AnimationPresets.breathing(from_scale, to_scale, duration)
        return self.animate_until_scene_end('scale', breathing_animation, repeat_delay,
                                          'restart', scene_duration)
    
    def get_animated_properties(self, time: float) -> Dict[str, Any]:
        """Get animated properties at the current time.
        
        Args:
            time: Current time in seconds
            
        Returns:
            Dictionary of animated property names and values
        """
        properties = {}
        
        # 位置のアニメーション
        animated_x = self.animation_manager.get_animated_value('x', time, self.base_x)
        animated_y = self.animation_manager.get_animated_value('y', time, self.base_y)
        if animated_x is not None:
            properties['x'] = animated_x
        if animated_y is not None:
            properties['y'] = animated_y
            
        # 透明度のアニメーション（background_alphaをベースとして使用）
        animated_alpha = self.animation_manager.get_animated_value('alpha', time, self.background_alpha)
        if animated_alpha is not None:
            properties['alpha'] = max(0, min(255, int(animated_alpha)))
            
        # スケールのアニメーション
        animated_scale = self.animation_manager.get_animated_value('scale', time, self.base_scale)
        if animated_scale is not None:
            properties['scale'] = max(0.0, animated_scale)
            
        # 回転のアニメーション
        animated_rotation = self.animation_manager.get_animated_value('rotation', time, self.rotation)
        if animated_rotation is not None:
            properties['rotation'] = animated_rotation
            
        # 色のアニメーション（背景色）
        if hasattr(self, 'color') and self.animation_manager.get_animated_value('color', time) is not None:
            animated_color = self.animation_manager.get_animated_value('color', time, getattr(self, 'color', (255, 255, 255)))
            properties['color'] = animated_color
            
        # 角丸半径のアニメーション
        animated_corner_radius = self.animation_manager.get_animated_value('corner_radius', time, self.corner_radius)
        if animated_corner_radius is not None:
            properties['corner_radius'] = max(0, animated_corner_radius)
            
        # ブラー強度のアニメーション
        animated_blur_strength = self.animation_manager.get_animated_value('blur_strength', time, self.blur_strength)
        if animated_blur_strength is not None:
            properties['blur_strength'] = max(0, animated_blur_strength)
            
        return properties
    
    def update_animated_properties(self, time: float) -> None:
        """Apply animated properties to current state.
        
        Args:
            time: Current time in seconds
        """
        animated_props = self.get_animated_properties(time)
        
        if 'x' in animated_props:
            self.x = animated_props['x']
        if 'y' in animated_props:
            self.y = animated_props['y']
        if 'alpha' in animated_props:
            self.background_alpha = animated_props['alpha']
        if 'scale' in animated_props:
            self.scale = animated_props['scale']
        if 'rotation' in animated_props:
            self.rotation = animated_props['rotation']
        if 'corner_radius' in animated_props:
            self.corner_radius = animated_props['corner_radius']
        if 'blur_strength' in animated_props:
            self.blur_strength = animated_props['blur_strength']
    
    def has_animations(self, time: Optional[float] = None) -> bool:
        """Check if element has animations.
        
        Args:
            time: Optional time to check for active animations
            
        Returns:
            True if element has animations (optionally active at given time)
        """
        if time is not None:
            return self.animation_manager.has_active_animations(time)
        return len(self.animation_manager.animations) > 0

    def calculate_size(self) -> None:
        """Pre-calculate box size (to be overridden by subclasses).
        
        This method should calculate and set the width and height attributes
        based on the element's content and styling properties.
        """
        pass

    def render(self, time: float) -> None:
        """Render the element (to be implemented by subclasses).
        
        Args:
            time: Current time in seconds for animation updates
        """
        # アニメーションプロパティを適用
        self.update_animated_properties(time)
        pass