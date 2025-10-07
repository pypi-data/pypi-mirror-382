# Playback TUI

A fully local terminal-based music player to play and download spotify/soundcloud playlists

## Features

- 🎵 Modern TUI interface with rich text and interactive elements
- 🎧 Browse and play local music playlists
- 📥 **Download playlists from Spotify and SoundCloud**
- ⏯️ Advanced playback controls (play/pause/skip/previous)
- 🔀 Shuffle and queue management
- 🎛️ Volume control and progress tracking
- ⌨️ Comprehensive keyboard shortcuts
- 🔍 Search functionality with command prompt
- 📊 Metadata display (artist, duration, album art)
- 🌍 **Cross-platform support** - works on Windows, macOS, and Linux
- 🎨 Modern terminal interface with visual selection highlighting

## Prerequisites

### Required Software
- **Python 3.10+** - Required for running the application
- **FFmpeg** - Required for downloading and processing audio from Spotify/SoundCloud

### Platform-Specific Prerequisites

#### macOS
Install via Homebrew:
```bash
brew install python@3.10 ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.10 python3-pip ffmpeg
```

#### Linux (Fedora/CentOS)
```bash
sudo dnf install python3.10 python3-pip ffmpeg
```

#### Windows
1. Install Python 3.10+ from [python.org](https://python.org)
2. Install FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html) or via chocolatey:
   ```cmd
   choco install ffmpeg
   ```

## Installation

1. Clone or download this repository
2. Install the package and dependencies:
   ```bash
   pip install -e .
   ```
   
   Or install dependencies manually:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
playback-tui
```

Or if installed in development mode:
```bash
python player.py
```

## Keyboard Shortcuts

### Main Navigation
- `Space` - Toggle play/pause
- `Enter` - Play selected song and generate new queue
- `Shift+Enter` - Add selected song to top of queue
- `Ctrl+C` - Exit application

### Playback Controls
- `Ctrl+Shift+Right` - Skip to next song
- `Ctrl+Shift+Left` - Previous song or restart current song
- `Ctrl+Shift+Up` - Page up in playlist
- `Ctrl+Shift+Down` - Page down in playlist
- `Cmd+Ctrl+Up` - Move to top of playlist (macOS)
- `Cmd+Ctrl+Down` - Move to bottom of playlist (macOS)

### Features
- `/` - Open command prompt/search
- `Ctrl+Shift+S` - Shuffle playlist
- `Ctrl+Shift+Q` - Open queue screen
- `Ctrl+Shift+T` - Open settings
- `Ctrl+Shift+D` - Open download status screen
- `Ctrl+Shift+U` - Download current playlist

### Modal Navigation
- `Escape` - Close current modal/screen
- `Up/Down` - Navigate lists
- `Enter` - Select item
- `Delete/Backspace` - Remove item (where applicable)

## Configuration

### Music Directory Structure
By default, the application looks for music in:
```
~/Playback-TUI/Playlists/
├── playlist1/
│   ├── song1.mp3
│   ├── song2.mp3
│   └── ...
├── playlist2/
│   ├── song3.mp3
│   └── ...
└── ...
```

You can customize playlist locations in the settings.

### Spotify Integration
For downloading playlists from Spotify, you'll need to:

1. Create a Spotify app at [developer.spotify.com](https://developer.spotify.com/dashboard)
2. Get your Client ID and Client Secret
3. Configure them in the application settings (`Ctrl+Shift+T`)

## Dependencies

### Python Packages
- `textual>=5.3.0` - Modern TUI framework
- `pygame>=2.6.0` - Audio playback
- `mutagen>=1.47.0` - Audio metadata
- `spotipy>=2.25.0` - Spotify API integration
- `yt-dlp>=2025.8.0` - YouTube/SoundCloud downloading
- `requests>=2.32.0` - HTTP requests

All dependencies are automatically installed when using `pip install -e .`

### System Requirements
- **FFmpeg** - Required for audio downloading and processing
- **Python 3.10+** - Required runtime environment

## Troubleshooting

### Audio Issues
- Ensure pygame can access your system's audio drivers
- On Linux, you may need to install additional audio libraries:
  ```bash
  sudo apt install libasound2-dev libpulse-dev
  ```

### Download Issues
- Verify FFmpeg is properly installed and in your PATH
- Check Spotify credentials are correctly configured
- Ensure internet connectivity for downloading
