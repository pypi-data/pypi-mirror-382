import math
from typing import Any, Dict, List, Union, Optional, Literal, Tuple
from abc import ABC, abstractmethod


class Animation(ABC):
    """Abstract base class for all animation types.
    
    This class provides the foundation for creating animations with timing control,
    progress calculation, and value interpolation. All animation implementations
    should inherit from this class.
    
    Attributes:
        duration: Duration of the animation in seconds
        start_time: Start time of the animation in seconds
        delay: Delay before animation starts in seconds
    """
    
    def __init__(self, duration: float = 1.0, start_time: float = 0.0, delay: float = 0.0) -> None:
        """Initialize a new Animation.
        
        Args:
            duration: Animation duration in seconds
            start_time: Animation start time in seconds
            delay: Delay before animation starts in seconds
        """
        self.duration: float = duration
        self.start_time: float = start_time
        self.delay: float = delay
    
    def is_active(self, time: float) -> bool:
        """Check if animation is active at the specified time.
        
        Args:
            time: Time in seconds to check
            
        Returns:
            True if animation is active at the given time
        """
        actual_start = self.start_time + self.delay
        return actual_start <= time < (actual_start + self.duration)
    
    def get_progress(self, time: float) -> float:
        """Calculate animation progress at the specified time.
        
        Args:
            time: Time in seconds
            
        Returns:
            Progress value between 0.0 and 1.0
        """
        if not self.is_active(time):
            actual_start = self.start_time + self.delay
            if time < actual_start:
                return 0.0
            else:
                return 1.0
        
        actual_start = self.start_time + self.delay
        elapsed = time - actual_start
        return min(1.0, max(0.0, elapsed / self.duration))
    
    @abstractmethod
    def calculate_value(self, progress: float) -> Any:
        """Calculate animation value based on progress.
        
        Args:
            progress: Animation progress (0.0 to 1.0)
            
        Returns:
            Interpolated value at the given progress
        """
        pass
    
    def get_value_at_time(self, time: float) -> Any:
        """Get animation value at the specified time.
        
        Args:
            time: Time in seconds
            
        Returns:
            Animation value at the given time
        """
        progress = self.get_progress(time)
        return self.calculate_value(progress)


class LinearAnimation(Animation):
    """Linear interpolation animation between start and end values.
    
    This animation provides smooth linear interpolation between two values
    over the specified duration.
    """
    
    def __init__(self, from_value: Union[float, int], to_value: Union[float, int], 
                 duration: float = 1.0, start_time: float = 0.0, delay: float = 0.0) -> None:
        """Initialize a linear animation.
        
        Args:
            from_value: Starting value
            to_value: Ending value
            duration: Animation duration in seconds
            start_time: Animation start time in seconds
            delay: Delay before animation starts in seconds
        """
        super().__init__(duration, start_time, delay)
        self.from_value: Union[float, int] = from_value
        self.to_value: Union[float, int] = to_value
    
    def calculate_value(self, progress: float) -> float:
        """Calculate linear interpolated value.
        
        Args:
            progress: Animation progress (0.0 to 1.0)
            
        Returns:
            Linearly interpolated value between from_value and to_value
        """
        return self.from_value + (self.to_value - self.from_value) * progress


class EaseInAnimation(Animation):
    """イーズイン（加速）アニメーション"""
    
    def __init__(self, from_value: Union[float, int], to_value: Union[float, int],
                 duration: float = 1.0, start_time: float = 0.0, delay: float = 0.0, power: float = 2.0):
        super().__init__(duration, start_time, delay)
        self.from_value = from_value
        self.to_value = to_value
        self.power = power
    
    def calculate_value(self, progress: float) -> float:
        """イーズイン補間で値を計算"""
        eased_progress = progress ** self.power
        return self.from_value + (self.to_value - self.from_value) * eased_progress


class EaseOutAnimation(Animation):
    """イーズアウト（減速）アニメーション"""
    
    def __init__(self, from_value: Union[float, int], to_value: Union[float, int],
                 duration: float = 1.0, start_time: float = 0.0, delay: float = 0.0, power: float = 2.0):
        super().__init__(duration, start_time, delay)
        self.from_value = from_value
        self.to_value = to_value
        self.power = power
    
    def calculate_value(self, progress: float) -> float:
        """イーズアウト補間で値を計算"""
        eased_progress = 1 - (1 - progress) ** self.power
        return self.from_value + (self.to_value - self.from_value) * eased_progress


class EaseInOutAnimation(Animation):
    """イーズイン・アウト（加速→減速）アニメーション"""
    
    def __init__(self, from_value: Union[float, int], to_value: Union[float, int],
                 duration: float = 1.0, start_time: float = 0.0, delay: float = 0.0, power: float = 2.0):
        super().__init__(duration, start_time, delay)
        self.from_value = from_value
        self.to_value = to_value
        self.power = power
    
    def calculate_value(self, progress: float) -> float:
        """イーズイン・アウト補間で値を計算"""
        if progress < 0.5:
            eased_progress = (progress * 2) ** self.power / 2
        else:
            eased_progress = 1 - ((1 - progress) * 2) ** self.power / 2
        return self.from_value + (self.to_value - self.from_value) * eased_progress


class BounceAnimation(Animation):
    """バウンス（跳ね返り）アニメーション"""
    
    def __init__(self, from_value: Union[float, int], to_value: Union[float, int],
                 duration: float = 1.0, start_time: float = 0.0, delay: float = 0.0, 
                 bounces: int = 3, bounce_height: float = 0.3):
        super().__init__(duration, start_time, delay)
        self.from_value = from_value
        self.to_value = to_value
        self.bounces = bounces
        self.bounce_height = bounce_height
    
    def calculate_value(self, progress: float) -> float:
        """バウンス効果で値を計算"""
        if progress >= 1.0:
            return self.to_value
        
        # バウンス効果の計算
        bounce_progress = progress
        if bounce_progress > 0.7:
            # 最終段階のバウンス
            t = (bounce_progress - 0.7) / 0.3
            bounce_offset = self.bounce_height * (1 - t) * math.sin(t * math.pi * self.bounces)
        else:
            # 通常のイーズアウト
            bounce_offset = 0
            
        base_progress = self._ease_out_cubic(progress)
        final_value = self.from_value + (self.to_value - self.from_value) * base_progress
        
        return final_value + bounce_offset * (self.to_value - self.from_value)
    
    def _ease_out_cubic(self, progress: float) -> float:
        """3次のイーズアウト"""
        return 1 - (1 - progress) ** 3


class SpringAnimation(Animation):
    """スプリング（ばね）アニメーション"""
    
    def __init__(self, from_value: Union[float, int], to_value: Union[float, int],
                 duration: float = 1.0, start_time: float = 0.0, delay: float = 0.0,
                 stiffness: float = 0.5, damping: float = 0.8):
        super().__init__(duration, start_time, delay)
        self.from_value = from_value
        self.to_value = to_value
        self.stiffness = stiffness
        self.damping = damping
    
    def calculate_value(self, progress: float) -> float:
        """スプリング効果で値を計算"""
        if progress >= 1.0:
            return self.to_value
        
        # スプリング振動の計算
        omega = self.stiffness * 2 * math.pi
        decay = math.exp(-self.damping * progress)
        spring_progress = 1 - decay * math.cos(omega * progress)
        
        return self.from_value + (self.to_value - self.from_value) * spring_progress


class KeyframeAnimation(Animation):
    """キーフレームアニメーション"""
    
    def __init__(self, keyframes: Dict[float, Union[float, int]],
                 duration: float = None, start_time: float = 0.0, delay: float = 0.0,
                 interpolation: str = 'linear'):
        """
        Args:
            keyframes: {時間: 値} の辞書。時間は0.0-1.0の範囲で正規化される
            duration: 総継続時間（Noneの場合はキーフレームから自動計算）
            interpolation: 補間方法 ('linear', 'ease_in', 'ease_out', 'ease_in_out')
        """
        if duration is None:
            duration = max(keyframes.keys()) if keyframes else 1.0
        super().__init__(duration, start_time, delay)
        
        # キーフレームを時間順にソート
        self.keyframes = sorted(keyframes.items())
        self.interpolation = interpolation
    
    def calculate_value(self, progress: float) -> float:
        """キーフレーム間の補間で値を計算"""
        if not self.keyframes:
            return 0
        
        # プログレスを正規化
        total_time = self.keyframes[-1][0] if self.keyframes[-1][0] > 0 else 1.0
        normalized_time = progress * total_time
        
        # 該当するキーフレーム区間を見つける
        for i, (time, value) in enumerate(self.keyframes):
            if normalized_time <= time:
                if i == 0:
                    return value
                
                # 前のキーフレームとの補間
                prev_time, prev_value = self.keyframes[i - 1]
                
                if time == prev_time:
                    return value
                
                # 補間係数を計算
                segment_progress = (normalized_time - prev_time) / (time - prev_time)
                segment_progress = self._apply_interpolation(segment_progress)
                
                return prev_value + (value - prev_value) * segment_progress
        
        # 最後のキーフレームを返す
        return self.keyframes[-1][1]
    
    def _apply_interpolation(self, t: float) -> float:
        """補間方法を適用"""
        if self.interpolation == 'ease_in':
            return t * t
        elif self.interpolation == 'ease_out':
            return 1 - (1 - t) * (1 - t)
        elif self.interpolation == 'ease_in_out':
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        else:  # linear
            return t


class RepeatingAnimation(Animation):
    """繰り返しアニメーション"""
    
    def __init__(self, base_animation: Animation, repeat_count: int = -1, 
                 repeat_delay: float = 0.0, repeat_mode: str = 'restart', 
                 until_scene_end: bool = False, scene_duration: float = None):
        """
        Args:
            base_animation: 繰り返すベースアニメーション
            repeat_count: 繰り返し回数（-1で無限、until_scene_endがTrueの場合は無視）
            repeat_delay: 各繰り返し間の遅延時間（秒）
            repeat_mode: 繰り返しモード ('restart', 'reverse', 'continue')
            until_scene_end: Trueの場合、シーン終了まで繰り返す
            scene_duration: シーンの継続時間（until_scene_endがTrueの場合に使用）
        """
        self.base_animation = base_animation
        self.repeat_count = repeat_count
        self.repeat_delay = repeat_delay
        self.repeat_mode = repeat_mode
        self.until_scene_end = until_scene_end
        self.scene_duration = scene_duration
        
        # 1サイクルの長さを計算
        self.cycle_duration = base_animation.duration + repeat_delay
        
        # 総継続時間を計算
        if until_scene_end and scene_duration is not None:
            total_duration = scene_duration
        elif repeat_count > 0:
            total_duration = self.cycle_duration * repeat_count - repeat_delay  # 最後のrepeat_delayは不要
        else:
            total_duration = float('inf')  # 無限繰り返し
        
        super().__init__(total_duration, base_animation.start_time, base_animation.delay)
    
    def calculate_value(self, progress: float) -> Any:
        """進行率に基づいて繰り返しアニメーションの値を計算"""
        if self.duration == float('inf'):
            # 無限繰り返しの場合はprogressを使わずに時刻ベースで計算
            return self._calculate_infinite_value(progress)
        
        # 有限時間での繰り返し
        current_time = progress * self.duration
        
        # 現在のサイクル番号を計算
        cycle_number = int(current_time // self.cycle_duration)
        time_in_cycle = current_time % self.cycle_duration
        
        # 遅延期間中かチェック
        if time_in_cycle > self.base_animation.duration:
            # 遅延期間中は最終値を返す
            if self.repeat_mode == 'reverse' and cycle_number % 2 == 1:
                return self.base_animation.calculate_value(0.0)  # 逆方向の最終値
            else:
                return self.base_animation.calculate_value(1.0)
        
        # ベースアニメーション実行中
        base_progress = time_in_cycle / self.base_animation.duration
        
        if self.repeat_mode == 'reverse' and cycle_number % 2 == 1:
            # 逆方向のサイクル
            base_progress = 1.0 - base_progress
        elif self.repeat_mode == 'continue':
            # 連続モード（前回の終了値から開始）
            # 基本的には同じ動作だが、将来の拡張で使用
            pass
        
        return self.base_animation.calculate_value(base_progress)
    
    def _calculate_infinite_value(self, progress: float) -> Any:
        """無限繰り返しの場合の値計算（主にテスト用）"""
        # 無限繰り返しの場合、progressは意味を持たないが、
        # テスト用に適当なサイクル計算を行う
        assumed_time = progress * 100  # 100秒と仮定
        cycle_number = int(assumed_time // self.cycle_duration)
        time_in_cycle = assumed_time % self.cycle_duration
        
        if time_in_cycle > self.base_animation.duration:
            if self.repeat_mode == 'reverse' and cycle_number % 2 == 1:
                return self.base_animation.calculate_value(0.0)
            else:
                return self.base_animation.calculate_value(1.0)
        
        base_progress = time_in_cycle / self.base_animation.duration
        
        if self.repeat_mode == 'reverse' and cycle_number % 2 == 1:
            base_progress = 1.0 - base_progress
        
        return self.base_animation.calculate_value(base_progress)
    
    def get_value_at_time(self, time: float) -> Any:
        """指定時刻での値を取得（繰り返し考慮）"""
        if not self.is_active(time):
            actual_start = self.start_time + self.delay
            if time < actual_start:
                return self.base_animation.calculate_value(0.0)
            else:
                return self.base_animation.calculate_value(1.0)
        
        # アクティブ期間での時刻計算
        actual_start = self.start_time + self.delay
        elapsed = time - actual_start
        
        # シーン終了まで繰り返しの場合、時間制限をチェック
        if self.until_scene_end and self.scene_duration is not None:
            if elapsed >= self.scene_duration:
                elapsed = self.scene_duration - 0.001  # 最後の値を返す
        
        # 現在のサイクル計算
        cycle_number = int(elapsed // self.cycle_duration)
        time_in_cycle = elapsed % self.cycle_duration
        
        # 有限繰り返しの場合、回数制限をチェック
        if self.repeat_count > 0 and cycle_number >= self.repeat_count:
            # 最終値を返す
            if self.repeat_mode == 'reverse' and (self.repeat_count - 1) % 2 == 1:
                return self.base_animation.calculate_value(0.0)
            else:
                return self.base_animation.calculate_value(1.0)
        
        # 遅延期間中かチェック
        if time_in_cycle > self.base_animation.duration:
            if self.repeat_mode == 'reverse' and cycle_number % 2 == 1:
                return self.base_animation.calculate_value(0.0)
            else:
                return self.base_animation.calculate_value(1.0)
        
        # ベースアニメーション実行中
        base_progress = time_in_cycle / self.base_animation.duration
        
        if self.repeat_mode == 'reverse' and cycle_number % 2 == 1:
            base_progress = 1.0 - base_progress
        
        return self.base_animation.calculate_value(base_progress)


class ColorAnimation(Animation):
    """色のアニメーション（RGB）"""
    
    def __init__(self, from_color: tuple, to_color: tuple,
                 duration: float = 1.0, start_time: float = 0.0, delay: float = 0.0,
                 interpolation: str = 'linear'):
        """
        Args:
            from_color: 開始色 (r, g, b)
            to_color: 終了色 (r, g, b)
            interpolation: 補間方法
        """
        super().__init__(duration, start_time, delay)
        self.from_color = from_color
        self.to_color = to_color
        self.interpolation = interpolation
    
    def calculate_value(self, progress: float) -> tuple:
        """RGB値の補間で色を計算"""
        if self.interpolation == 'ease_in':
            progress = progress ** 2
        elif self.interpolation == 'ease_out':
            progress = 1 - (1 - progress) ** 2
        elif self.interpolation == 'ease_in_out':
            progress = 2 * progress ** 2 if progress < 0.5 else 1 - 2 * (1 - progress) ** 2
        
        r = int(self.from_color[0] + (self.to_color[0] - self.from_color[0]) * progress)
        g = int(self.from_color[1] + (self.to_color[1] - self.from_color[1]) * progress)
        b = int(self.from_color[2] + (self.to_color[2] - self.from_color[2]) * progress)
        
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))


# 便利な定数とプリセット
class AnimationPresets:
    """よく使用されるアニメーションのプリセット"""
    
    @staticmethod
    def fade_in(duration: float = 1.0, delay: float = 0.0) -> LinearAnimation:
        """フェードイン"""
        return LinearAnimation(0, 255, duration, delay=delay)
    
    @staticmethod
    def fade_out(duration: float = 1.0, delay: float = 0.0) -> LinearAnimation:
        """フェードアウト"""  
        return LinearAnimation(255, 0, duration, delay=delay)
    
    @staticmethod
    def slide_in_from_left(distance: float = 200, duration: float = 1.0, delay: float = 0.0) -> EaseOutAnimation:
        """左からスライドイン"""
        return EaseOutAnimation(-distance, 0, duration, delay=delay)
    
    @staticmethod
    def slide_in_from_right(distance: float = 200, duration: float = 1.0, delay: float = 0.0) -> EaseOutAnimation:
        """右からスライドイン"""
        return EaseOutAnimation(distance, 0, duration, delay=delay)
    
    @staticmethod 
    def scale_up(from_scale: float = 0.0, to_scale: float = 1.0, duration: float = 1.0, delay: float = 0.0) -> EaseOutAnimation:
        """拡大アニメーション"""
        return EaseOutAnimation(from_scale, to_scale, duration, delay=delay)
    
    @staticmethod
    def bounce_in(duration: float = 1.5, delay: float = 0.0) -> BounceAnimation:
        """バウンスして登場"""
        return BounceAnimation(0, 1, duration, delay=delay, bounces=3, bounce_height=0.3)
    
    @staticmethod
    def spring_in(duration: float = 2.0, delay: float = 0.0) -> SpringAnimation:
        """スプリングで登場"""
        return SpringAnimation(0, 1, duration, delay=delay, stiffness=0.6, damping=0.8)
    
    @staticmethod
    def pulse(from_scale: float = 1.0, to_scale: float = 1.3, duration: float = 1.0, delay: float = 0.0) -> KeyframeAnimation:
        """パルス（鼓動）アニメーション"""
        keyframes = {
            0.0: from_scale,
            0.5: to_scale,
            1.0: from_scale
        }
        return KeyframeAnimation(keyframes, duration, delay=delay, interpolation='ease_in_out')
    
    @staticmethod
    def breathing(from_scale: float = 1.0, to_scale: float = 1.1, duration: float = 2.0, delay: float = 0.0) -> KeyframeAnimation:
        """呼吸のようなゆっくりとした拡大縮小"""
        keyframes = {
            0.0: from_scale,
            0.5: to_scale,
            1.0: from_scale
        }
        return KeyframeAnimation(keyframes, duration, delay=delay, interpolation='ease_in_out')
    
    @staticmethod
    def wiggle(amplitude: float = 10.0, duration: float = 0.5, delay: float = 0.0) -> KeyframeAnimation:
        """小刻みな振動アニメーション"""
        keyframes = {
            0.0: 0,
            0.25: amplitude,
            0.5: -amplitude,
            0.75: amplitude,
            1.0: 0
        }
        return KeyframeAnimation(keyframes, duration, delay=delay, interpolation='linear')


# アニメーション管理クラス
class AnimationManager:
    """複数のアニメーションを統合管理"""
    
    def __init__(self):
        self.animations: Dict[str, List[Animation]] = {}
    
    def add_animation(self, property_name: str, animation: Animation):
        """プロパティにアニメーションを追加"""
        if property_name not in self.animations:
            self.animations[property_name] = []
        self.animations[property_name].append(animation)
    
    def get_animated_value(self, property_name: str, time: float, base_value: Any = None):
        """指定プロパティのアニメーション値を取得"""
        if property_name not in self.animations:
            return base_value
        
        current_value = base_value
        for animation in self.animations[property_name]:
            # RepeatingAnimationの特別な処理
            if isinstance(animation, RepeatingAnimation):
                if animation.is_active(time) or (animation.until_scene_end and animation.scene_duration is not None):
                    current_value = animation.get_value_at_time(time)
                    break
            else:
                if animation.is_active(time):
                    current_value = animation.get_value_at_time(time)
                    break  # 最初に見つかったアクティブなアニメーションを使用
        
        return current_value
    
    def has_active_animations(self, time: float) -> bool:
        """指定時刻でアクティブなアニメーションがあるかチェック"""
        for animations in self.animations.values():
            for animation in animations:
                if animation.is_active(time):
                    return True
        return False
    
    def clear_animations(self, property_name: str = None):
        """アニメーションをクリア"""
        if property_name:
            self.animations.pop(property_name, None)
        else:
            self.animations.clear()