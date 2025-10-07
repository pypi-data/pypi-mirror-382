#!/usr/bin/env python3
"""
Streamlined playlist downloader for Spotify and SoundCloud.
Simplified version focused on core functionality.
"""

import os
import sys
import json
import time
import random
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp


def get_config_dir() -> Path:
    """Get the configuration directory for playback-tui."""
    config_dir = Path.home() / ".config" / "playback-tui"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_default_config_path(filename: str) -> str:
    """Get the default path for a config file."""
    return str(get_config_dir() / filename)


def parse_music_filename(filepath: str) -> tuple[str, str]:
    """
    Enhanced parsing function for music filenames that handles various formats.
    
    Common SoundCloud/music filename patterns:
    - "Artist - Song"
    - "Artist1, Artist2 - Song" (multiple artists)
    - "Artist – Song" (em dash)
    - "Artist: Song" 
    - "Song by Artist"
    - "Song (Artist Remix)"
    - "Song ft. Artist"
    - "Song feat Artist"
    - "Artist | Song"
    - Just "Song Title"
    
    Returns:
        tuple: (song_title, artist_name) where artist_name may contain multiple artists separated by commas
    """
    import re
    
    def normalize_artists(artist_string: str) -> str:
        """Normalize multiple artists to comma-separated format."""
        if not artist_string:
            return "Unknown Artist"
        
        # Replace common separators with commas
        artist_string = re.sub(r'\s*[&+]\s*', ', ', artist_string)  # & or + to comma
        artist_string = re.sub(r'\s*,\s*', ', ', artist_string)  # normalize comma spacing
        artist_string = re.sub(r'\s*;\s*', ', ', artist_string)  # semicolon to comma
        
        # Clean up multiple commas
        artist_string = re.sub(r',+', ',', artist_string)
        artist_string = artist_string.strip(', ')
        
        return artist_string if artist_string else "Unknown Artist"
    
    filename = os.path.basename(filepath)
    name_without_ext = os.path.splitext(filename)[0].strip()
    
    # Clean up common problematic characters and normalize whitespace
    name_without_ext = re.sub(r'\s+', ' ', name_without_ext)  # Multiple spaces to single
    name_without_ext = name_without_ext.replace('_', ' ')  # Underscores to spaces
    
    # Special Pattern: "Artist1 - Artist2 - Song Title" (two artists followed by song)
    # Check for exactly 2 dashes with the first two parts having no spaces
    dash_count = name_without_ext.count(' - ')
    if dash_count == 2:
        parts = name_without_ext.split(' - ', 2)  # Split into 3 parts
        if len(parts) == 3:
            part1, part2, part3 = [p.strip() for p in parts]
            # Check if first two parts have no spaces (single words/names)
            if (' ' not in part1 and ' ' not in part2 and 
                len(part1) > 0 and len(part2) > 0 and len(part3) > 0):
                # Treat first two as artists, third as song
                combined_artists = f"{part1}, {part2}"
                return part3, combined_artists
    
    # Pattern 1: "Artist - Song" or "Artist – Song" (hyphen or em dash)
    dash_patterns = [r' - ', r' – ', r' — ']
    for pattern in dash_patterns:
        if pattern in name_without_ext:
            parts = name_without_ext.split(pattern, 1)
            if len(parts) == 2:
                artist = parts[0].strip()
                song = parts[1].strip()
                # Ensure both parts have reasonable content
                if len(artist) > 0 and len(song) > 0 and len(artist) < 100:
                    normalized_artist = normalize_artists(artist)
                    return song, normalized_artist
    
    # Pattern 2: "Artist: Song"
    if ':' in name_without_ext and name_without_ext.count(':') == 1:
        parts = name_without_ext.split(':', 1)
        if len(parts) == 2:
            artist = parts[0].strip()
            song = parts[1].strip()
            if len(artist) > 0 and len(song) > 0 and len(artist) < 100:
                normalized_artist = normalize_artists(artist)
                return song, normalized_artist
    
    # Pattern 3: "Artist | Song"
    if ' | ' in name_without_ext:
        parts = name_without_ext.split(' | ', 1)
        if len(parts) == 2:
            artist = parts[0].strip()
            song = parts[1].strip()
            if len(artist) > 0 and len(song) > 0 and len(artist) < 100:
                normalized_artist = normalize_artists(artist)
                return song, normalized_artist
    
    # Pattern 4: "Song by Artist"
    by_match = re.search(r'^(.+?)\s+by\s+(.+)$', name_without_ext, re.IGNORECASE)
    if by_match:
        song = by_match.group(1).strip()
        artist = by_match.group(2).strip()
        if len(artist) > 0 and len(song) > 0:
            normalized_artist = normalize_artists(artist)
            return song, normalized_artist
    
    # Pattern 5: "Song (Artist Remix)" or "Song (featuring Artist)"
    remix_patterns = [
        r'^(.+?)\s*\((.+?)\s+remix\)$',
        r'^(.+?)\s*\((.+?)\s+mix\)$',
        r'^(.+?)\s*\((.+?)\s+edit\)$',
        r'^(.+?)\s*\((.+?)\s+version\)$'
    ]
    for pattern in remix_patterns:
        match = re.search(pattern, name_without_ext, re.IGNORECASE)
        if match:
            song = match.group(1).strip()
            artist = match.group(2).strip()
            if len(artist) > 0 and len(song) > 0:
                normalized_artist = normalize_artists(artist)
                return f"{song} ({artist} Remix)", normalized_artist
    
    # Pattern 6: "Song ft. Artist" or "Song feat Artist"
    ft_patterns = [
        r'^(.+?)\s+ft\.?\s+(.+)$',
        r'^(.+?)\s+feat\.?\s+(.+)$',
        r'^(.+?)\s+featuring\s+(.+)$'
    ]
    for pattern in ft_patterns:
        match = re.search(pattern, name_without_ext, re.IGNORECASE)
        if match:
            song = match.group(1).strip()
            featured_artist = match.group(2).strip()
            if len(featured_artist) > 0 and len(song) > 0:
                normalized_artist = normalize_artists(featured_artist)
                return f"{song} ft. {featured_artist}", normalized_artist
    
    # Pattern 7: Try to extract artist from parentheses at end: "Song (Artist)"
    paren_match = re.search(r'^(.+?)\s*\(([^)]+)\)$', name_without_ext)
    if paren_match:
        song = paren_match.group(1).strip()
        potential_artist = paren_match.group(2).strip()
        # Only use if it looks like an artist name (not a year, genre, etc.)
        if (len(potential_artist) > 0 and len(potential_artist) < 50 and 
            not re.match(r'^\d{4}$', potential_artist) and  # Not a year
            not potential_artist.lower() in ['official', 'hq', 'hd', 'audio', 'video', 'lyrics']):
            normalized_artist = normalize_artists(potential_artist)
            return song, normalized_artist
    
    # Fallback: treat entire name as song with Unknown Artist
    return name_without_ext.strip(), "Unknown Artist"


class PlaylistDownloader:
    """Handles downloading playlists from Spotify and SoundCloud."""
    
    def __init__(self, spotify_credentials: Dict[str, str]):
        """Initialize the downloader with Spotify credentials."""
        self.spotify_credentials = spotify_credentials
        self._setup_spotify_client()
        
        # User agents for rotation to avoid rate limiting
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ]
        self.current_ua_index = 0
    
    def _setup_spotify_client(self):
        """Setup Spotify client with credentials."""
        try:
            # Set environment variables for Spotify
            os.environ['SPOTIPY_CLIENT_ID'] = self.spotify_credentials.get('SPOTIFY_CLIENT_ID', '')
            if os.environ['SPOTIPY_CLIENT_ID'] == "":
                raise Exception("No Spotify credentials found")
            os.environ['SPOTIPY_CLIENT_SECRET'] = self.spotify_credentials.get('SPOTIFY_CLIENT_SECRET', '')
            if os.environ['SPOTIPY_CLIENT_ID'] == "":
                raise Exception("No Spotify credentials found")
            
            self.spotify = spotipy.Spotify(
                client_credentials_manager=SpotifyClientCredentials()
            )
        except Exception as e:
            print(f"Failed to setup Spotify client: {e}")
            print(f"Passed Spotify credentials: {self.spotify_credentials}")
            self.spotify = None
    
    def _get_next_user_agent(self) -> str:
        """Get the next user agent in rotation."""
        ua = self.user_agents[self.current_ua_index]
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        return ua
    
    def _clean_filename(self, filename: str) -> str:
        """Clean filename to remove problematic characters."""
        # Remove or replace problematic characters
        filename = filename.replace("/", "_").replace("\\", "_")
        filename = "".join(c if c.isalnum() or c in "- " else "_" for c in filename)
        # Remove multiple consecutive underscores
        while "__" in filename:
            filename = filename.replace("__", "_")
        return filename.strip("_")
    
    def _clean_soundcloud_filename(self, filepath: str) -> Optional[str]:
        """Clean up SoundCloud downloaded filename for better parsing."""
        if not os.path.exists(filepath):
            return None
        
        try:
            # First check if the file matches the specific pattern we want to handle
            filename = os.path.basename(filepath)
            name_without_ext = os.path.splitext(filename)[0].strip()
            
            # Check for "Artist1 - Artist2 - Song Title" pattern
            if name_without_ext.count(' - ') == 2:
                parts = name_without_ext.split(' - ', 2)
                if len(parts) == 3:
                    part1, part2, part3 = [p.strip() for p in parts]
                    # If first two parts have no spaces (single words), combine them
                    if (' ' not in part1 and ' ' not in part2 and 
                        len(part1) > 0 and len(part2) > 0 and len(part3) > 0):
                        
                        dir_path = os.path.dirname(filepath)
                        file_ext = os.path.splitext(filepath)[1]
                        
                        # Create new filename with combined artists
                        clean_part1 = self._clean_filename(part1)
                        clean_part2 = self._clean_filename(part2)
                        clean_part3 = self._clean_filename(part3)
                        
                        new_filename = f"{clean_part1}, {clean_part2} - {clean_part3}{file_ext}"
                        new_filepath = os.path.join(dir_path, new_filename)
                        
                        # Only rename if the new name is different and doesn't exist
                        if new_filepath != filepath and not os.path.exists(new_filepath):
                            os.rename(filepath, new_filepath)
                            return new_filepath
            
            # Fall back to general parsing and cleaning
            song, artist = parse_music_filename(filepath)
            
            # If we have both song and artist info and it's not "Unknown Artist"
            if artist != "Unknown Artist" and len(song) > 0:
                # Create a cleaner filename in "Artist - Song" format
                dir_path = os.path.dirname(filepath)
                file_ext = os.path.splitext(filepath)[1]
                
                # Clean the artist and song names
                clean_artist = self._clean_filename(artist)
                clean_song = self._clean_filename(song)
                
                new_filename = f"{clean_artist} - {clean_song}{file_ext}"
                new_filepath = os.path.join(dir_path, new_filename)
                
                # Only rename if the new name is different and doesn't exist
                if new_filepath != filepath and not os.path.exists(new_filepath):
                    os.rename(filepath, new_filepath)
                    return new_filepath
            
            return filepath
        except Exception as e:
            # If anything goes wrong, just return the original path
            print(f"Warning: Could not clean filename {filepath}: {e}")
            return filepath
    
    def _clean_empty_files(self, output_dir: str, progress_callback=None) -> None:
        """Remove any 0MB or corrupted audio files from the output directory."""
        from pathlib import Path
        
        source_dir = Path(output_dir)
        audio_files = list(source_dir.glob("*.mp3")) + list(source_dir.glob("*.m4a")) + list(source_dir.glob("*.opus"))
        
        removed_count = 0
        for audio_file in audio_files:
            try:
                # Check if file is empty (0 bytes) or very small (less than 1KB, likely corrupted)
                if audio_file.stat().st_size < 1024:
                    audio_file.unlink()
                    removed_count += 1
                    message = f"Removed empty/corrupted file: {audio_file.name}"
                    print(message, flush=True)
                    if progress_callback:
                        progress_callback(0, 0, message)
                    
                # Also try to check if the file is a valid audio file using ffprobe
                else:
                    cmd = [
                        'ffprobe',
                        '-v', 'error',
                        '-select_streams', 'a:0',
                        '-show_entries', 'stream=codec_type',
                        '-of', 'default=noprint_wrappers=1:nokey=1',
                        str(audio_file)
                    ]
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                        if result.returncode != 0 or 'audio' not in result.stdout:
                            audio_file.unlink()
                            removed_count += 1
                            message = f"Removed invalid audio file: {audio_file.name}"
                            print(message, flush=True)
                            if progress_callback:
                                progress_callback(0, 0, message)
                    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                        # If ffprobe fails or times out, the file might be corrupted
                        audio_file.unlink()
                        removed_count += 1
                        message = f"Removed potentially corrupted file: {audio_file.name}"
                        print(message, flush=True)
                        if progress_callback:
                            progress_callback(0, 0, message)
                            
            except Exception as e:
                print(f"Warning: Error checking file {audio_file.name}: {e}", flush=True)
        
        if removed_count > 0:
            message = f"Cleaned up {removed_count} empty or corrupted files"
            print(message, flush=True)
            if progress_callback:
                progress_callback(0, 0, message)

    def _normalize_audio_volume(self, output_dir: str, progress_callback=None) -> None:
        """Normalize volume of all MP3 files in the output directory."""
        from pathlib import Path
        
        source_dir = Path(output_dir)
        mp3_files = list(source_dir.glob("*.mp3"))
        
        if not mp3_files:
            return
        
        for mp3_file in mp3_files:
            try:
                # Create temporary file for normalized audio
                temp_file = mp3_file.with_suffix('.tmp.mp3')
                
                # Use ffmpeg loudnorm filter to normalize audio
                cmd = [
                    'ffmpeg',
                    '-i', str(mp3_file),
                    '-af', 'loudnorm=I=-23:TP=-2:LRA=7',
                    '-ar', '44100',
                    '-b:a', '192k',
                    '-y',
                    str(temp_file)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                # Replace original with normalized version
                mp3_file.unlink()
                temp_file.rename(mp3_file)
                
                # Log with timestamp in [hour:minute:second] format
                message = f"Normalized: {mp3_file.name}"
                print(message, flush=True)
                
                # Also send through progress callback if available
                if progress_callback:
                    progress_callback(0, 0, message)
                
            except (subprocess.CalledProcessError, Exception):
                # Clean up temp file if it exists
                if temp_file.exists():
                    temp_file.unlink()
                # Skip failed normalizations silently
    
    def get_spotify_tracks(self, playlist_url: str) -> List[Dict]:
        """Get tracks from a Spotify playlist."""
        if not self.spotify:
            raise Exception("Spotify client not initialized")
        
        # Extract playlist ID from URL
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        
        print("Fetching Spotify playlist tracks...")
        results = self.spotify.playlist_tracks(playlist_id)
        tracks = results["items"]
        
        # Handle pagination
        while results["next"]:
            results = self.spotify.next(results)
            tracks.extend(results["items"])
        
        print(f"Found {len(tracks)} tracks in playlist")
        return tracks
    
    def _download_with_yt_dlp(self, search_term: str, output_path: str) -> bool:
        """Download a single track using yt-dlp."""
        # Set FFmpeg location in environment
        import shutil
        ffmpeg_path = shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'
        ffprobe_path = shutil.which('ffprobe') or '/opt/homebrew/bin/ffprobe'
        
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "outtmpl": f"{output_path}.%(ext)s",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "http_headers": {"User-Agent": self._get_next_user_agent()},
            "ffmpeg_location": ffmpeg_path,
        }
        
        # Also add to PATH as backup
        import os
        old_path = os.environ.get('PATH', '')
        os.environ['PATH'] = f"/opt/homebrew/bin:{old_path}"
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"ytsearch:{search_term}"])
                return True
        except Exception as e:
            print(f"Failed to download {search_term}: {e}")
            return False
        finally:
            # Restore original PATH
            os.environ['PATH'] = old_path
    
    def download_spotify_playlist(self, playlist_url: str, output_dir: str, 
                                 progress_callback=None) -> Dict[str, int]:
        """Download all tracks from a Spotify playlist."""
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get tracks
        tracks = self.get_spotify_tracks(playlist_url)
        
        successful = 0
        failed = 0
        skipped = 0
        
        for i, item in enumerate(tracks):
            track = item.get("track")
            if not track:
                skipped += 1
                continue
            
            track_name = track["name"]
            artists = [artist["name"] for artist in track["artists"]]
            artist = artists[0]  # Use primary artist
            
            # Create safe filename
            safe_filename = self._clean_filename(f"{artist} - {track_name}")
            output_path = os.path.join(output_dir, safe_filename)
            
            # Check if file already exists
            if os.path.exists(f"{output_path}.mp3"):
                skipped += 1
                if progress_callback:
                    progress_callback(i + 1, len(tracks), f"Skipped: {artist} - {track_name}")
                continue
            
            if progress_callback:
                progress_callback(i + 1, len(tracks), f"Downloading: {artist} - {track_name}")
            
            # Try to download
            search_term = f"{artist} - {track_name}"
            success = self._download_with_yt_dlp(search_term, output_path)
            
            if success and os.path.exists(f"{output_path}.mp3"):
                successful += 1
                print(f"✓ Downloaded: {artist} - {track_name}")
            else:
                failed += 1
                print(f"✗ Failed: {artist} - {track_name}")
                # Log failed downloads
                with open(os.path.join(output_dir, "failed_downloads.txt"), "a") as f:
                    f.write(f"{artist} - {track_name}\n")
            
            # Small delay to avoid rate limiting
            time.sleep(random.uniform(0.5, 1.5))
        
        # Normalize volume of all downloaded MP3 files
        self._normalize_audio_volume(output_dir, progress_callback)
        
        # Clean up any empty or corrupted files
        self._clean_empty_files(output_dir, progress_callback)
        
        return {
            "total": len(tracks),
            "successful": successful,
            "failed": failed,
            "skipped": skipped
        }
    
    def download_soundcloud_likes(self, soundcloud_url: str, output_dir: str,
                                 progress_callback=None) -> Dict[str, int]:
        """Download SoundCloud likes."""
        # Import required modules
        import shutil
        import os
        from pathlib import Path
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        if progress_callback:
            progress_callback(0, 0, "Starting SoundCloud download...")
        
        # Set FFmpeg location
        ffmpeg_path = shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'
        
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            # Use better template that tries to extract artist info when available
            "outtmpl": os.path.join(output_dir, "%(uploader|Unknown Artist)s - %(title)s.%(ext)s"),
            "quiet": False,
            "ignoreerrors": True,
            "http_headers": {"User-Agent": self._get_next_user_agent()},
            "sleep_interval": 1,
            "max_sleep_interval": 3,
            "ffmpeg_location": ffmpeg_path,
        }
        
        # Add to PATH as backup
        old_path = os.environ.get('PATH', '')
        os.environ['PATH'] = f"/opt/homebrew/bin:{old_path}"
        
        successful = 0
        
        def progress_hook(d):
            nonlocal successful
            if d['status'] == 'finished':
                successful += 1
                filename = d.get('filename', 'Unknown')
                
                # Clean up the downloaded filename if needed
                if filename != 'Unknown':
                    self._clean_soundcloud_filename(filename)
                
                track_title = os.path.basename(filename)
                if progress_callback:
                    progress_callback(successful, 0, f"Downloaded: {track_title}")
        
        ydl_opts['progress_hooks'] = [progress_hook]
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([soundcloud_url])
        except Exception as e:
            print(f"SoundCloud download error: {e}")
        finally:
            # Restore original PATH
            os.environ['PATH'] = old_path
        
        # Convert remaining .opus and .m4a files to .mp3
        source_dir = Path(output_dir)
        audio_extensions = ['.opus', '.m4a']
        audio_files = []
        
        for ext in audio_extensions:
            audio_files.extend(source_dir.glob(f"*{ext}"))
        
        if audio_files:
            for audio_file in audio_files:
                output_file = audio_file.with_suffix('.mp3')
                
                # Skip if mp3 already exists
                if output_file.exists():
                    continue
                
                cmd = [
                    'ffmpeg',
                    '-i', str(audio_file),
                    '-codec:a', 'libmp3lame',
                    '-b:a', '192k',
                    '-y',
                    str(output_file)
                ]
                
                try:
                    subprocess.run(cmd, capture_output=True, text=True, check=True)
                    # Log with timestamp in [hour:minute:second] format
                    message = f"Converted: {output_file.name}"
                    print(message, flush=True)
                    
                    # Also send through progress callback if available
                    if progress_callback:
                        progress_callback(0, 0, message)
                    
                    # Remove original file after successful conversion
                    audio_file.unlink()
                except subprocess.CalledProcessError:
                    pass
        
        # Normalize volume of all MP3 files
        self._normalize_audio_volume(output_dir, progress_callback)
        
        # Clean up any empty or corrupted files
        self._clean_empty_files(output_dir, progress_callback)
        
        return {
            "total": successful,
            "successful": successful,
            "failed": 0,
            "skipped": 0
        }


def download_playlist(playlist_name: str, settings_file: Optional[str] = None, 
                     spotify_env_file: Optional[str] = None,
                     progress_callback=None) -> bool:
    """
    Download a playlist by name using settings files.
    
    Args:
        playlist_name: Name of the playlist from settings
        settings_file: Path to playlist settings JSON file
        spotify_env_file: Path to Spotify credentials JSON file
        progress_callback: Optional callback function for progress updates
    
    Returns:
        True if download was successful, False otherwise
    """
    try:
        # Use default config paths if not provided
        settings_file = settings_file or get_default_config_path("playlist_settings.json")
        spotify_env_file = spotify_env_file or get_default_config_path("spotify_env.json")
        
        # Load playlist settings
        with open(settings_file, 'r') as f:
            playlists = json.load(f)
        
        if playlist_name not in playlists:
            print(f"Playlist '{playlist_name}' not found in settings")
            return False
        
        playlist_config = playlists[playlist_name]
        playlist_url = playlist_config["url"]
        output_dir = os.path.expanduser(playlist_config["directory"])
        
        # Load Spotify credentials
        with open(spotify_env_file, 'r') as f:
            spotify_credentials = json.load(f)
        
        # Initialize downloader
        downloader = PlaylistDownloader(spotify_credentials)
        
        print(f"Starting download for playlist: {playlist_name}")
        print(f"URL: {playlist_url}")
        print(f"Output directory: {output_dir}")
        
        # Download based on platform
        if "soundcloud.com" in playlist_url:
            results = downloader.download_soundcloud_likes(playlist_url, output_dir, progress_callback)
        else:  # Assume Spotify
            results = downloader.download_spotify_playlist(playlist_url, output_dir, progress_callback)
        
        # Print summary
        print(f"\n{'='*50}")
        print(f"Download Complete for: {playlist_name}")
        print(f"Total tracks: {results['total']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed: {results['failed']}")
        print(f"Skipped: {results['skipped']}")
        print(f"{'='*50}")
        
        return True
        
    except Exception as e:
        print(f"Error downloading playlist: {e}")
        return False


if __name__ == "__main__":
    # Command line usage
    if len(sys.argv) != 2:
        print("Usage: python downloader.py <playlist_name>")
        sys.exit(1)
    
    playlist_name = sys.argv[1]
    success = download_playlist(playlist_name)
    sys.exit(0 if success else 1)
