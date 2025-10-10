import os
import cv2
import numpy as np
from typing import List, Literal
from tqdm import tqdm
from OpenGL.GL import *
from OpenGL.GLU import *
from .scene_element import Scene

# Pygameの警告を抑制
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

# オーディオ処理用ライブラリの試行インポート
try:
    import subprocess
    import json
    HAS_FFMPEG = True
except ImportError:
    HAS_FFMPEG = False


def has_audio_stream(video_path: str) -> bool:
    """Check if a video file has an audio stream using ffprobe.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        True if the video has at least one audio stream, False otherwise
    """
    if not HAS_FFMPEG:
        return False
    
    if not os.path.exists(video_path):
        return False
    
    try:
        # Use ffprobe to check for audio streams
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_streams', '-select_streams', 'a', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                streams = data.get('streams', [])
                return len(streams) > 0
            except json.JSONDecodeError:
                return False
        return False
        
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        # Fallback: try to use OpenCV to detect audio properties
        try:
            cap = cv2.VideoCapture(video_path)
            if cap.isOpened():
                # Try to get audio properties - if they exist, there's likely audio
                audio_fourcc = cap.get(cv2.CAP_PROP_AUDIO_STREAM)
                cap.release()
                return audio_fourcc != -1.0 and audio_fourcc != 0.0
            cap.release()
        except:
            pass
        
        return False


class MasterScene:
    """マスターシーンクラス - 全体の動画を管理"""
    def __init__(self, output_filename: str = "output_video.mp4", width: int = 1920, height: int = 1080, fps: int = 60, quality: Literal["low", "medium", "high"] = "medium"):
        self.width = width
        self.height = height
        self.fps = fps
        self.quality = quality  # "low", "medium", "high"
        self.scenes: List[Scene] = []
        self.total_duration = 0.0
        self.output_filename = output_filename
        self.audio_elements = []  # オーディオ要素を追跡
        self._has_content_at_start = False  # Track if master scene has content at time 0
        
        # 品質設定に基づいてスーパーサンプリング倍率を設定
        self.quality_multipliers = {
            "low": 1,     # 1x (現在の動作)
            "medium": 2,  # 2x スーパーサンプリング
            "high": 4     # 4x スーパーサンプリング
        }
        self.render_scale = self.quality_multipliers.get(quality, 2)
        self.render_width = width * self.render_scale
        self.render_height = height * self.render_scale
    
    def add(self, scene: Scene, layer: Literal["top", "bottom"] = "top"):
        """シーンを追加
        
        Args:
            scene: 追加するシーン
            layer: "top" を指定すると一番上に追加（最後にレンダリング）、"bottom" を指定すると一番下に追加（最初にレンダリング）
        """
        # シーンのstart_timeが明示的に設定されていない場合（Noneの場合）、
        # 前のシーンの終了時間を開始時間として設定（逐次再生）
        if scene.start_time is None:
            # シーンが0秒時点でコンテンツを持っているかチェック
            scene_has_content_at_start = self._scene_has_content_at_time(scene, 0.0)
            
            if scene_has_content_at_start and not self._has_content_at_start:
                # シーンに0秒時点でコンテンツがあり、マスターシーンにまだ0秒コンテンツがない場合
                # シーンを0秒から開始させる
                scene.start_time = 0.0
                self._has_content_at_start = True
            elif self.scenes:
                # 通常の逐次配置
                last_scene = self.scenes[-1]
                last_scene_start = last_scene.start_time if last_scene.start_time is not None else 0.0
                scene.start_time = last_scene_start + last_scene.duration
            else:
                # 最初のシーンでstart_timeが設定されていない場合は0から開始
                scene.start_time = 0.0
        
        # Add scene based on layer parameter
        if layer == "bottom":
            self.scenes.insert(0, scene)
        else:  # layer == "top" (default)
            self.scenes.append(scene)
        # 全体の継続時間を更新
        scene_end_time = scene.start_time + scene.duration
        self.total_duration = max(self.total_duration, scene_end_time)
        
        # オーディオ要素を収集
        self._collect_audio_elements(scene)
        
        # マスターシーン全体の長さに合わせてBGMの持続時間を更新
        self._update_master_bgm_durations()
        return self
    
    def _scene_has_content_at_time(self, scene, time: float) -> bool:
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
    
    def _update_master_bgm_durations(self):
        """マスターシーン全体の長さに合わせてBGMの持続時間を更新"""
        from .audio_element import AudioElement
        for audio_element in self.audio_elements:
            if isinstance(audio_element, AudioElement) and audio_element.loop_until_scene_end:
                # マスターシーン全体の長さまでBGMを拡張
                if self.total_duration > audio_element.duration:
                    audio_element.duration = self.total_duration
    
    def _collect_audio_elements(self, scene: Scene, time_offset: float = 0.0):
        """シーンからオーディオ要素を収集（ネストされたシーンにも対応）
        
        Args:
            scene: Audio elements to collect from
            time_offset: Cumulative time offset from parent scenes
        """
        from .audio_element import AudioElement
        from .video_element import VideoElement
        import copy
        
        # Calculate the total time offset for this scene
        scene_start = scene.start_time if scene.start_time is not None else 0.0
        total_offset = time_offset + scene_start
        
        for element in scene.elements:
            if isinstance(element, Scene):
                # Recursively collect from nested scenes
                self._collect_audio_elements(element, total_offset)
            elif isinstance(element, AudioElement):
                # Create a copy to avoid modifying the original element's start_time
                audio_copy = copy.deepcopy(element)
                # Adjust timing only on the copy
                audio_copy.start_time += total_offset
                self.audio_elements.append(audio_copy)
            elif isinstance(element, VideoElement):
                # Ensure the video element's audio element is created
                element._ensure_audio_element()
                audio_element = element.get_audio_element()
                if audio_element is not None:
                    # Create a copy to avoid modifying the original element's start_time
                    audio_copy = copy.deepcopy(audio_element)
                    # Adjust timing only on the copy
                    audio_copy.start_time += total_offset
                    # Only add if the video actually has audio
                    self.audio_elements.append(audio_copy)
    
    def set_output(self, filename: str):
        """出力ファイル名を設定"""
        self.output_filename = filename
        return self
    
    def set_quality(self, quality: str):
        """レンダリング品質を設定
        
        Args:
            quality: 品質レベル ("low", "medium", "high")
                - "low": 1x レンダリング (高速、低品質)
                - "medium": 2x スーパーサンプリング (バランス型)
                - "high": 4x スーパーサンプリング (高品質、低速)
        
        Returns:
            Self for method chaining
        """
        if quality not in self.quality_multipliers:
            print(f"Warning: Invalid quality '{quality}'. Using 'medium' instead.")
            quality = "medium"
        
        self.quality = quality
        self.render_scale = self.quality_multipliers[quality]
        self.render_width = self.width * self.render_scale
        self.render_height = self.height * self.render_scale
        return self
    
    def _apply_quality_to_scene(self, scene):
        """シーンの要素に品質設定を適用（ネストされたシーンにも対応）"""
        from .text_element import TextElement
        from .image_element import ImageElement
        from .video_element import VideoElement
        
        for element in scene.elements:
            if isinstance(element, Scene):
                # Recursively apply quality to nested scenes
                self._apply_quality_to_scene(element)
            elif isinstance(element, TextElement):
                if not hasattr(element, 'quality_scale') or element.quality_scale != self.render_scale:
                    element.quality_scale = self.render_scale
                    # テクスチャを再作成するためのフラグをリセット
                    element.texture_created = False
                    # サイズも再計算する
                    element.calculate_size()
            # TODO: ImageElementとVideoElementも同様に対応
    
    def _init_opengl(self):
        """OpenGLの初期設定"""
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        # 座標系を設定（左上が原点、ピクセル座標系）
        # 重要: 座標系は出力解像度のまま維持（スケールしない）
        # これにより既存の要素の位置指定が正しく動作する
        glOrtho(0, self.width, self.height, 0, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # ビューポートを高解像度レンダリング用に設定
        glViewport(0, 0, self.render_width, self.render_height)
        
        # ブレンディングを有効にしてアルファ値を使用可能に
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    def _setup_video_writer(self):
        """動画書き込み設定"""
        # オーディオ要素がある場合は一時ファイル、ない場合は指定ファイル名
        if self.audio_elements:
            # 一時ファイル名を作成
            base_name = os.path.splitext(self.output_filename)[0]
            ext = os.path.splitext(self.output_filename)[1]
            full_path = f"{base_name}_temp_video_only{ext}"
        else:
            full_path = self.output_filename
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        video_writer = cv2.VideoWriter(full_path, fourcc, self.fps, (self.width, self.height))
        
        if not video_writer.isOpened():
            raise Exception(f"動画ファイル {full_path} を作成できませんでした")
        
        return video_writer, full_path
    
    def _capture_frame(self):
        """現在の画面をキャプチャ"""
        # 高解像度でキャプチャ（アルファチャンネル込み）
        pixels = glReadPixels(0, 0, self.render_width, self.render_height, GL_RGBA, GL_UNSIGNED_BYTE)
        image = np.frombuffer(pixels, dtype=np.uint8)
        image = image.reshape((self.render_height, self.render_width, 4))
        image = np.flipud(image)  # OpenGLは左下が原点なので上下反転
        
        # RGBAからBGRAに変換
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)
        
        # スーパーサンプリングの場合は出力解像度にダウンスケール
        if self.render_scale > 1:
            image = cv2.resize(image, (self.width, self.height), interpolation=cv2.INTER_AREA)
        
        # MP4出力用にアルファチャンネルを除去してBGRに変換
        # 透明部分は黒背景とブレンドされる
        bgr_image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        
        return bgr_image
    
    def _create_audio_mix(self, video_path: str):
        """FFmpegを使ってビデオにオーディオを追加"""
        if not self.audio_elements:
            print("No audio elements found, skipping audio mixing")
            return video_path
        
        if not HAS_FFMPEG:
            print("Warning: subprocess not available, cannot mix audio")
            return video_path
        
        # FFmpegが利用可能かチェック
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: FFmpeg not found, cannot mix audio")
            print("Install FFmpeg to enable audio mixing:")
            print("  macOS: brew install ffmpeg")
            print("  Ubuntu: sudo apt install ffmpeg")
            return video_path
        
        final_output = self.output_filename
        
        # 複数のオーディオファイルを処理するためのコマンド構築
        cmd = ['ffmpeg', '-y', '-i', video_path]
        
        # 存在するオーディオファイルのみを追加（タイミング情報はfilter_complexで処理）
        valid_audio_files = []
        
        # オーディオタイミング検証および音声ストリーム確認
        for audio_element in self.audio_elements:
            if not os.path.exists(audio_element.audio_path):
                print(f"Warning: Audio file not found, skipping: {audio_element.audio_path}")
                continue
            
            # Check if the file has actual audio streams (for video files)
            if not has_audio_stream(audio_element.audio_path):
                print(f"Warning: No audio stream found in file, skipping: {audio_element.audio_path}")
                continue
            
            # 警告チェック
            if audio_element.start_time + audio_element.duration > self.total_duration + 0.1:  # 0.1s tolerance
                print(f"  WARNING: Audio extends beyond scene duration ({self.total_duration:.2f}s)")
            if audio_element.start_time < 0:
                print(f"  WARNING: Audio starts before scene start")
            
            # BGMモードでループが必要な場合は複数回入力を追加
            if getattr(audio_element, 'loop_until_scene_end', False) and audio_element.duration > audio_element.original_duration:
                # 必要なループ回数を計算
                loop_count = int((audio_element.duration / audio_element.original_duration) + 0.99)
                
                # 同じファイルを複数回入力として追加
                for i in range(loop_count):
                    cmd.extend(['-i', audio_element.audio_path])
                
            else:
                # 通常の単一入力
                cmd.extend(['-i', audio_element.audio_path])
            
            valid_audio_files.append(audio_element)
        
        if not valid_audio_files:
            print("No valid audio files found, keeping video-only output")
            return video_path
        
        # オーディオファイルのミキシング処理
        if len(valid_audio_files) == 1:
            # 単一オーディオファイルの場合、volume調整とduration制限を適用
            audio_element = valid_audio_files[0]
            volume = audio_element.volume if hasattr(audio_element, 'volume') else 1.0
            is_muted = getattr(audio_element, 'is_muted', False)

            # ミュート状態の場合は音量を0にする
            if is_muted:
                volume = 0.0
            
            # BGMのループが必要な場合
            if getattr(audio_element, 'loop_until_scene_end', False) and audio_element.duration > audio_element.original_duration:
                # 複数の入力ストリームを連結してループを作成
                loop_count = int((audio_element.duration / audio_element.original_duration) + 0.99)

                # 複数のストリームを連結
                input_streams = []
                for i in range(1, loop_count + 1):  # 1から開始（0はビデオ）
                    input_streams.append(f"[{i}:a]")
                
                # 連結フィルター
                concat_filter = ''.join(input_streams) + f"concat=n={loop_count}:v=0:a=1[looped];"
                
                # 遅延処理
                start_time = audio_element.start_time
                filter_chain = "[looped]"
                if start_time > 0:
                    delay_ms = int(start_time * 1000)
                    filter_chain += f"adelay={delay_ms}|{delay_ms},"
                
                # 音量調整と時間制限
                filter_chain += f"volume={volume},atrim=end={self.total_duration}"
                
                full_filter = concat_filter + filter_chain
                cmd.extend(['-filter_complex', full_filter, '-c:v', 'copy', '-c:a', 'aac', 
                           '-t', str(self.total_duration), final_output])
            else:
                # 単一ファイル、ループなしの場合
                filter_chain = ""
                
                # 遅延処理
                start_time = audio_element.start_time
                if start_time > 0:
                    delay_ms = int(start_time * 1000)
                    filter_chain += f"adelay={delay_ms}|{delay_ms},"
                
                # 音量調整と時間制限
                filter_chain += f"volume={volume},atrim=end={self.total_duration}"
                
                cmd.extend(['-filter:a', filter_chain, '-c:v', 'copy', '-c:a', 'aac', 
                           '-t', str(self.total_duration), final_output])
        else:
            # オーディオストリームをミキシングするfilter_complexを構築（adelayでタイミング制御）
            audio_inputs = []
            for i, audio_element in enumerate(valid_audio_files, 1):  # index 1から開始（index 0はビデオ）
                # 各オーディオストリームに対してvolume、delay、duration制限を適用
                volume = audio_element.volume if hasattr(audio_element, 'volume') else 1.0
                start_time = audio_element.start_time
                delay_ms = int(start_time * 1000)  # milliseconds for adelay

                # ミュート状態の場合は音量を0にする
                if getattr(audio_element, 'is_muted', False):
                    volume = 0.0
                
                # フィルターチェーンを構築
                filter_chain = f"[{i}:a]"
                
                # BGMの場合は最初にループ処理を適用
                if getattr(audio_element, 'loop_until_scene_end', False) and audio_element.duration > audio_element.original_duration:
                    # 必要な長さまでループさせる
                    # aloopを使用して無限ループし、その後atrimで必要な長さに切り取る
                    filter_chain += f"aloop=loop=-1:size={int(44100 * audio_element.original_duration)},atrim=end={audio_element.duration},"

                # 遅延を適用（0秒の場合はスキップ）
                if delay_ms > 0:
                    filter_chain += f"adelay={delay_ms}|{delay_ms},"  # ステレオの場合両チャンネルに適用
                
                # 音量調整を適用
                filter_chain += f"volume={volume}"
                
                # 最終的な時間制限を適用（全体の動画時間を超えないように）
                if getattr(audio_element, 'loop_until_scene_end', False):
                    filter_chain += f",atrim=end={self.total_duration}"
                else:
                    pass
                
                audio_inputs.append(f"{filter_chain}[a{i}]")
            
            # 全てのオーディオストリームをミキシング（正規化を無効にして音量を保持）
            mix_inputs = ''.join([f"[a{i}]" for i in range(1, len(valid_audio_files) + 1)])
            filter_complex = ';'.join(audio_inputs) + f";{mix_inputs}amix=inputs={len(valid_audio_files)}:normalize=0[aout]"
            
            cmd.extend(['-filter_complex', filter_complex, '-map', '0:v', '-map', '[aout]', 
                       '-c:v', 'copy', '-c:a', 'aac', '-t', str(self.total_duration), final_output])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # 一時ファイルを削除
                if os.path.exists(video_path) and "temp_video_only" in video_path:
                    os.remove(video_path)
                return final_output
            else:
                print(f"FFmpeg error: {result.stderr}")
                print("Keeping video-only output")
                return video_path
        except Exception as e:
            print(f"Error during audio mixing: {e}")
            print("Keeping video-only output")
            return video_path
    
    def render(self):
        """動画をレンダリング"""
        # 環境設定（ウィンドウを非表示）
        os.environ['SDL_VIDEODRIVER'] = 'cocoa'
        os.environ['SDL_VIDEO_WINDOW_POS'] = '-1000,-1000'
        
        # Pygameを初期化
        pygame.init()
        
        # OpenGLウィンドウを作成（高解像度レンダリング用）
        screen = pygame.display.set_mode(
            (self.render_width, self.render_height), 
            pygame.DOUBLEBUF | pygame.OPENGL | pygame.HIDDEN
        )
        
        # OpenGLを初期化
        self._init_opengl()
        
        # 動画書き込み設定
        video_writer, video_path = self._setup_video_writer()
        
        try:
            total_frames = int(self.total_duration * self.fps)
            
            # 品質設定をすべてのシーンに適用（一度だけ）
            for scene in self.scenes:
                self._apply_quality_to_scene(scene)

            # tqdmでプログレスバーを表示
            with tqdm(total=total_frames, desc="Rendering", unit="frames") as pbar:
                for frame_num in range(total_frames):
                    current_time = frame_num / self.fps
                    
                    # 画面をクリア
                    glClear(GL_COLOR_BUFFER_BIT)
                    
                    # 全シーンをレンダリング
                    for scene in self.scenes:
                        scene.render(current_time)
                    
                    # 描画を確定
                    pygame.display.flip()
                    
                    # フレームをキャプチャして動画に書き込み
                    frame = self._capture_frame()
                    video_writer.write(frame)
                    
                    # プログレスバーを更新
                    pbar.update(1)
            
        finally:
            # クリーンアップ
            video_writer.release()
            pygame.quit()
            
            # オーディオミキシング（ビデオ作成後）
            if self.audio_elements:
                final_output = self._create_audio_mix(video_path)