# FrameKit

A powerful Python-based video editor for programmatic video generation using OpenGL rendering. Create professional videos with text overlays, images, video clips, and audio mixing through a clean, fluent API.

## Features

- **🎬 Video Composition**: Combine text, images, and video clips into professional videos
- **🎨 OpenGL Rendering**: High-performance graphics rendering with real-time effects
- **🎵 Audio Integration**: Multi-track audio mixing with BGM support and FFmpeg integration
- **📝 Rich Text**: Advanced text rendering with custom fonts, backgrounds, borders, and Japanese support
- **🎞️ Video Elements**: Frame-accurate video playback with audio control and visual effects
- **🎯 Animation System**: Smooth animations for position, scale, rotation, and opacity
- **🔄 Fluent API**: Method chaining for clean, readable code
- **🌐 Cross-Platform**: Works on macOS, Linux, and Windows

## Installation
```
pip install framekit
```

## Core Components

### VideoBase
Base class for all video elements providing:
- Position and timing control
- Fluent interface methods
- Animation support
- Visual effects (corner radius, borders)

### Elements

- **TextElement**: Rich text with custom fonts, backgrounds, borders, and multi-line support
- **ImageElement**: Static image rendering with scaling and visual effects
- **VideoElement**: Video clip playback with frame-accurate timing and audio control
- **AudioElement**: Audio playback with volume control, fading, and BGM looping

### Composition

- **Scene**: Container for grouping elements with relative timing
- **MasterScene**: Main composition manager handling OpenGL context and video export
