import os
from typing import Optional, Dict, Any, Union
import numpy as np
from .video_base import VideoBase

# オーディオライブラリのインポートを試行
try:
    import mutagen
    from mutagen import File as MutagenFile
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False


class AudioElement(VideoBase):
    """Audio element for playing audio files with volume control and fade effects.
    
    This class extends VideoBase to provide audio playback capabilities with support for
    various audio formats, volume control, fade in/out effects, muting, and BGM looping.
    
    Attributes:
        audio_path: Path to the audio file to play
        volume: Current volume level (0.0-1.0)
        original_volume: Original volume level before modifications
        sample_rate: Audio sample rate in Hz
        total_samples: Total number of audio samples
        channels: Number of audio channels
        current_audio_data: Current audio data buffer
        fade_in_duration: Fade-in duration in seconds
        fade_out_duration: Fade-out duration in seconds
        is_muted: Whether audio is currently muted
        loop_until_scene_end: Whether to loop audio until scene ends (BGM mode)
        original_duration: Original duration of the audio file
    """
    
    def __init__(self, audio_path: str, volume: float = 1.0) -> None:
        """Initialize a new AudioElement.
        
        Args:
            audio_path: Path to the audio file (supports common formats like MP3, WAV, etc.)
            volume: Initial volume level (0.0 = silent, 1.0 = full volume)
        """
        super().__init__()
        self.audio_path: str = audio_path
        self.volume: float = volume
        self.original_volume: float = volume
        self.sample_rate: int = 44100
        self.total_samples: int = 0
        self.channels: int = 2
        self.current_audio_data: Optional[np.ndarray] = None
        self.fade_in_duration: float = 0.0
        self.fade_out_duration: float = 0.0
        self.is_muted: bool = False
        self.loop_until_scene_end: bool = False
        self.original_duration: float = 0.0
        self._load_audio_info()
        # 初期化時にサイズを計算（オーディオは視覚的要素がないため0）
        self.calculate_size()
    
    def _load_audio_info(self) -> None:
        """Load audio file information and duration.
        
        This method attempts to load audio metadata using mutagen or librosa libraries.
        Falls back to a default duration if no audio libraries are available.
        """
        if not os.path.exists(self.audio_path):
            print(f"Warning: Audio file not found: {self.audio_path}")
            return
        
        try:
            # mutagenを使ってオーディオ情報を取得
            if HAS_MUTAGEN:
                audio_file = MutagenFile(self.audio_path)
                if audio_file is not None and hasattr(audio_file, 'info'):
                    self.duration = float(audio_file.info.length)
                    self.original_duration = self.duration
                    return
            
            # librosaを使ってオーディオ情報を取得
            if HAS_LIBROSA:
                try:
                    y, sr = librosa.load(self.audio_path, sr=None)
                    self.duration = len(y) / sr
                    self.original_duration = self.duration
                    self.sample_rate = sr
                    return
                except Exception as librosa_error:
                    print(f"Librosa failed: {librosa_error}")
            
            # フォールバック: ファイル名からの推定またはデフォルト値
            print(f"Warning: Could not determine audio duration for {self.audio_path}")
            print("Install 'mutagen' or 'librosa' for proper audio file support:")
            print("  pip3 install mutagen")
            print("  pip3 install librosa")
            self.duration = 10.0  # デフォルト値
            self.original_duration = self.duration
            
        except Exception as e:
            print(f"Error loading audio info {self.audio_path}: {e}")
            self.duration = 10.0  # デフォルト値
            self.original_duration = self.duration
    
    def set_volume(self, volume: float) -> 'AudioElement':
        """Set audio volume level.
        
        Args:
            volume: Volume level (0.0 = silent, 1.0 = full volume, >1.0 = amplified)
            
        Returns:
            Self for method chaining
        """
        self.volume = max(0.0, volume)  # Only clamp the lower bound, allow amplification
        self.original_volume = self.volume
        return self
    
    def set_fade_in(self, duration: float) -> 'AudioElement':
        """Set fade-in duration.
        
        Args:
            duration: Fade-in duration in seconds (0.0 = no fade-in)
            
        Returns:
            Self for method chaining
        """
        self.fade_in_duration = max(0.0, duration)
        return self
    
    def set_fade_out(self, duration: float) -> 'AudioElement':
        """Set fade-out duration.
        
        Args:
            duration: Fade-out duration in seconds (0.0 = no fade-out)
            
        Returns:
            Self for method chaining
        """
        self.fade_out_duration = max(0.0, duration)
        return self
    
    def mute(self) -> 'AudioElement':
        """Mute the audio track.
        
        Returns:
            Self for method chaining
        """
        self.is_muted = True
        return self
    
    def unmute(self) -> 'AudioElement':
        """Unmute the audio track.
        
        Returns:
            Self for method chaining
        """
        self.is_muted = False
        return self
    
    def set_loop_until_scene_end(self, loop: bool = True) -> 'AudioElement':
        """Set whether to loop audio until scene ends (BGM mode).
        
        Args:
            loop: If True, audio will loop continuously until the scene ends
            
        Returns:
            Self for method chaining
        """
        self.loop_until_scene_end = loop

        return self
    
    def update_duration_for_scene(self, scene_duration: float) -> None:
        """Update duration to match scene duration when in BGM loop mode.
        
        Args:
            scene_duration: Duration of the containing scene in seconds
        """
        if self.loop_until_scene_end:
            # BGMはシーンの長さに合わせて調整（ループまたは強制終了）
            if scene_duration > 0:  # シーンに他の要素がある場合のみ
                self.duration = scene_duration
    
    def get_effective_volume(self, audio_time: float) -> float:
        """Calculate effective volume considering fade in/out and mute status.
        
        Args:
            audio_time: Time within the audio track in seconds
            
        Returns:
            Effective volume level (>=0.0) after applying all effects
        """
        if self.is_muted:
            return 0.0
        
        effective_volume = self.volume
        
        # Apply fade in
        if self.fade_in_duration > 0 and audio_time < self.fade_in_duration:
            fade_in_factor = audio_time / self.fade_in_duration
            effective_volume *= fade_in_factor
        
        # Apply fade out
        if self.fade_out_duration > 0:
            fade_out_start = self.duration - self.fade_out_duration
            if audio_time > fade_out_start:
                remaining_time = self.duration - audio_time
                fade_out_factor = remaining_time / self.fade_out_duration
                effective_volume *= fade_out_factor
        
        return max(0.0, effective_volume)  # Only clamp lower bound, allow amplification
    
    def _get_audio_at_time(self, audio_time: float) -> None:
        """Get audio data at specific time (placeholder implementation).
        
        Args:
            audio_time: Time within the audio track in seconds
            
        Returns:
            None (placeholder for external audio library integration)
        """
        # オーディオの場合、実際の音声データの処理は
        # 外部のオーディオライブラリ（pygame, pyaudio等）に依存するため
        # ここではプレースホルダーとして実装
        return None
    
    def render(self, time: float) -> None:
        """Render audio (no visual output for audio elements).
        
        Args:
            time: Current time in seconds (used for timing calculations)
        """
        if not self.is_visible_at(time):
            return
        
        # Calculate audio time (time within the audio clip)
        audio_time = time - self.start_time
        
        # オーディオの場合、視覚的なレンダリングは不要
        # 実際のオーディオ再生は外部システムで処理される
        pass
    
    def get_audio_data_at_time(self, time: float) -> Optional[Dict[str, Any]]:
        """Get audio data and metadata for external audio system.
        
        Args:
            time: Current time in seconds
            
        Returns:
            Dictionary containing audio metadata and parameters, or None if not active
        """
        if not self.is_visible_at(time):
            return None
        
        
        # Calculate audio time (time within the audio clip)
        audio_time = time - self.start_time
        
        # Calculate effective volume with fade effects
        effective_volume = self.get_effective_volume(audio_time)
        
        # Return audio metadata for external processing
        return {
            'audio_path': self.audio_path,
            'audio_time': audio_time,
            'volume': effective_volume,
            'original_volume': self.original_volume,
            'start_time': self.start_time,
            'duration': self.duration,
            'is_muted': self.is_muted,
            'fade_in_duration': self.fade_in_duration,
            'fade_out_duration': self.fade_out_duration
        }
    
    def calculate_size(self) -> None:
        """Pre-calculate audio box size (no visual elements for audio).
        
        Audio elements have no visual representation, so width and height are set to 0.
        """
        # オーディオ要素は視覚的な表示がないため、サイズは0
        self.width = 0
        self.height = 0
    
    def __del__(self) -> None:
        """Destructor to clean up audio resources.
        
        Placeholder for audio resource cleanup. Actual implementation depends
        on the specific audio library being used.
        """
        # オーディオ要素用のクリーンアップ
        pass