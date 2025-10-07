#!/usr/bin/env python3
"""
Simple Music Player with playlist and song browsing
Uses Textual for terminal UI and pygame for audio playback.
Press Space to play/pause, Enter to select items.
"""

import os
import glob
import time
import threading
import json
import subprocess
import sys
import random
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path
from datetime import datetime

import pygame
from mutagen import File as MutagenFile
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Static, Label, DataTable, Input, ListView, ListItem, Button, TextArea, ProgressBar
from textual.containers import Vertical, Horizontal, Container
from textual.timer import Timer
from textual.screen import ModalScreen
from rich.text import Text
from pynput import keyboard

# Import our downloader module and improved parsing function
from downloader import parse_music_filename
from downloader import download_playlist


class GlobalHotkeyManager:
    """Manages global hotkeys for media control on macOS."""
    
    def __init__(self, app_instance):
        self.app_instance = app_instance
        self.listener = None
        self.running = False
        self.pressed_keys = set()  # Track currently pressed keys for combinations
    
    def start(self):
        """Start the global hotkey listener in a background thread."""
        if self.running:
            return
        
        self.running = True
        
        def on_press(key):
            try:
                # Debug: Print all key presses to help diagnose
                print(f"Global key pressed: {key} (type: {type(key)})")
                
                # Handle media keys with multiple detection methods
                key_handled = False
                
                # Method 1: Direct comparison with Key constants
                try:
                    if key == keyboard.Key.media_play_pause:
                        print("Media play/pause detected (direct)")
                        self.app_instance.call_from_thread(self.app_instance._global_toggle_playback)
                        key_handled = True
                    elif key == keyboard.Key.media_next:
                        print("Media next detected (direct)")
                        self.app_instance.call_from_thread(self.app_instance._global_skip_song)
                        key_handled = True
                    elif key == keyboard.Key.media_previous:
                        print("Media previous detected (direct)")
                        self.app_instance.call_from_thread(self.app_instance._global_previous_song)
                        key_handled = True
                except AttributeError:
                    pass
                
                # Method 2: Check by string representation (fallback for macOS)
                if not key_handled:
                    key_str = str(key).lower()
                    if 'play_pause' in key_str or 'media_play_pause' in key_str:
                        print("Media play/pause detected (string)")
                        self.app_instance.call_from_thread(self.app_instance._global_toggle_playback)
                        key_handled = True
                    elif 'next' in key_str or 'media_next' in key_str:
                        print("Media next detected (string)")
                        self.app_instance.call_from_thread(self.app_instance._global_skip_song)
                        key_handled = True
                    elif 'previous' in key_str or 'media_previous' in key_str:
                        print("Media previous detected (string)")
                        self.app_instance.call_from_thread(self.app_instance._global_previous_song)
                        key_handled = True
                
                # Method 3: Handle F7, F8, F9 as alternatives (common on Mac keyboards)
                if not key_handled:
                    if key == keyboard.Key.f7:
                        print("F7 detected (previous)")
                        self.app_instance.call_from_thread(self.app_instance._global_previous_song)
                        key_handled = True
                    elif key == keyboard.Key.f8:
                        print("F8 detected (play/pause)")
                        self.app_instance.call_from_thread(self.app_instance._global_toggle_playback)
                        key_handled = True
                    elif key == keyboard.Key.f9:
                        print("F9 detected (next)")
                        self.app_instance.call_from_thread(self.app_instance._global_skip_song)
                        key_handled = True
                
                # Method 4: Handle Command+Arrow combinations as additional alternatives
                if not key_handled and hasattr(key, 'vk') and hasattr(keyboard, '_MODIFIER_MASK'):
                    # This is for raw key codes - might catch media keys that aren't detected above
                    vk = getattr(key, 'vk', None)
                    if vk:
                        print(f"Raw key code: {vk}")
                        # Common macOS media key codes
                        if vk == 16:  # Play/Pause
                            print("Media play/pause detected (raw)")
                            self.app_instance.call_from_thread(self.app_instance._global_toggle_playback)
                        elif vk == 17:  # Next
                            print("Media next detected (raw)")
                            self.app_instance.call_from_thread(self.app_instance._global_skip_song)
                        elif vk == 18:  # Previous
                            print("Media previous detected (raw)")
                            self.app_instance.call_from_thread(self.app_instance._global_previous_song)
                    
            except AttributeError as ae:
                print(f"AttributeError in key handling: {ae}")
            except Exception as e:
                # Log any other errors but don't crash
                print(f"Global hotkey error: {e}")
        
        def on_release(key):
            try:
                self.pressed_keys.discard(key)
            except:
                pass
        
        # Also track pressed keys for combinations
        def enhanced_on_press(key):
            self.pressed_keys.add(key)
            
            # Check for Command+Left/Right combinations (alternative for media keys)
            if keyboard.Key.cmd in self.pressed_keys or keyboard.Key.cmd_l in self.pressed_keys or keyboard.Key.cmd_r in self.pressed_keys:
                if key == keyboard.Key.left:
                    print("Command+Left detected (previous)")
                    self.app_instance.call_from_thread(self.app_instance._global_previous_song)
                    return
                elif key == keyboard.Key.right:
                    print("Command+Right detected (next)")
                    self.app_instance.call_from_thread(self.app_instance._global_skip_song)
                    return
                elif key == keyboard.Key.space:
                    print("Command+Space detected (play/pause)")
                    self.app_instance.call_from_thread(self.app_instance._global_toggle_playback)
                    return
            
            # Call the original handler
            on_press(key)
        
        # Start the keyboard listener in a daemon thread
        self.listener = keyboard.Listener(on_press=enhanced_on_press, on_release=on_release)
        self.listener.daemon = True
        self.listener.start()
    
    def stop(self):
        """Stop the global hotkey listener."""
        if self.listener and self.running:
            self.running = False
            self.listener.stop()
            self.listener = None


def get_config_dir() -> Path:
    """Get the configuration directory for playback-tui."""
    config_dir = Path.home() / ".config" / "playback-tui"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_default_config_path(filename: str) -> str:
    """Get the default path for a config file."""
    return str(get_config_dir() / filename)





class PlaylistSettings:
    """Manages playlist settings and Spotify credentials with persistent storage."""
    
    def __init__(self, settings_file: Optional[str] = None, spotify_env_file: Optional[str] = None):
        # Use default config directory if not specified
        self.settings_file = settings_file or get_default_config_path("playlist_settings.json")
        self.spotify_env_file = spotify_env_file or get_default_config_path("spotify_env.json")
        self.playlists: Dict[str, Dict[str, str]] = {}
        self.spotify_credentials: Dict[str, str] = {}
        self.load_settings()
        self.load_spotify_credentials()
    
    def load_settings(self) -> None:
        """Load settings from JSON file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    # Check if data has old format with 'playlists' key
                    if 'playlists' in data:
                        self.playlists = data['playlists']
                    else:
                        # New flat format - data is directly the playlists
                        self.playlists = data
            else:
                # Initialize with empty playlists for new installations
                self.playlists = {
                    "Welcome": {
                        "url": "https://open.spotify.com/playlist/1mgNfBnhTIabiACn0NfQiQ?si=l_cDUgmKTb6ZiwRcpsr4sg",
                        "directory": str(Path.home() / "Playback-TUI" / "Playlists" / "Welcome")
                    }
                }
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.playlists = {}
    
    def save_settings(self) -> None:
        """Save settings to JSON file."""
        try:
            # Save playlists directly as flat JSON structure
            with open(self.settings_file, 'w') as f:
                json.dump(self.playlists, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def add_playlist(self, name: str, url: str, directory: str) -> bool:
        """Add a new playlist."""
        if name and name not in self.playlists:
            self.playlists[name] = {"url": url, "directory": directory}
            self.save_settings()
            return True
        return False
    
    def update_playlist(self, old_name: str, new_name: str, url: str, directory: str) -> bool:
        """Update an existing playlist."""
        if old_name in self.playlists:
            if old_name != new_name and new_name in self.playlists:
                return False  # New name already exists
            
            # Remove old entry if name changed
            if old_name != new_name:
                del self.playlists[old_name]
            
            self.playlists[new_name] = {"url": url, "directory": directory}
            self.save_settings()
            return True
        return False
    
    def delete_playlist(self, name: str) -> bool:
        """Delete a playlist."""
        if name in self.playlists:
            del self.playlists[name]
            self.save_settings()
            return True
        return False
    
    def get_playlist_names(self) -> List[str]:
        """Get list of playlist names."""
        return sorted(self.playlists.keys())
    
    def get_playlist(self, name: str) -> Optional[Dict[str, str]]:
        """Get playlist configuration by name."""
        return self.playlists.get(name)
    
    def get_all_playlists(self) -> Dict[str, Dict[str, str]]:
        """Get all playlist configurations."""
        return self.playlists.copy()
    
    def load_spotify_credentials(self) -> None:
        """Load Spotify credentials from JSON file."""
        try:
            if os.path.exists(self.spotify_env_file):
                with open(self.spotify_env_file, 'r') as f:
                    data = json.load(f)
                    self.spotify_credentials = data
            else:
                # Initialize with placeholder credentials for new installations
                self.spotify_credentials = {
                    "SPOTIFY_CLIENT_ID": "",
                    "SPOTIFY_CLIENT_SECRET": ""
                }
                self.save_spotify_credentials()
        except Exception as e:
            print(f"Error loading Spotify credentials: {e}")
            self.spotify_credentials = {}
    
    def save_spotify_credentials(self) -> None:
        """Save Spotify credentials to JSON file."""
        try:
            with open(self.spotify_env_file, 'w') as f:
                json.dump(self.spotify_credentials, f, indent=2)
        except Exception as e:
            print(f"Error saving Spotify credentials: {e}")
    
    def get_spotify_credentials(self) -> Dict[str, str]:
        """Get Spotify credentials."""
        return self.spotify_credentials.copy()
    
    def update_spotify_credentials(self, credentials: Dict[str, str]) -> bool:
        """Update Spotify credentials."""
        try:
            self.spotify_credentials = credentials
            self.save_spotify_credentials()
            return True
        except Exception as e:
            print(f"Error updating Spotify credentials: {e}")
            return False


class MusicPlayer:
    """Simple music player using pygame."""
    
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        self.song_path: Optional[str] = None
        self.is_playing: bool = False
        self.is_paused: bool = False
        self.position: float = 0.0
        self.duration: float = 0.0
        self._position_timer: Optional[Timer] = None
        self.song_end_callback: Optional[callable] = None
    
    def get_song_name(self) -> str:
        """Get the song filename."""
        if self.song_path:
            return os.path.basename(self.song_path)
        return "------------"
    
    def load_and_play(self, song_path: str) -> bool:
        """Load and play a new song from the beginning."""
        if not os.path.exists(song_path):
            return False
        
        try:
            self.stop()  # Stop current song
            self.song_path = song_path
            pygame.mixer.music.load(self.song_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            self.position = 0.0
            
            # Get actual duration from audio metadata
            try:
                audio_file = MutagenFile(self.song_path)
                if audio_file is not None and hasattr(audio_file, 'info') and hasattr(audio_file.info, 'length'):
                    self.duration = audio_file.info.length
                else:
                    # Fallback to file size estimation if metadata reading fails
                    file_size = os.path.getsize(self.song_path)
                    self.duration = file_size / (128 * 1024 / 8)
            except:
                self.duration = 180.0
            
            return True
        except pygame.error:
            return False
    
    def toggle_playback(self) -> bool:
        """Toggle between play and pause."""
        if not self.song_path:
            return False
            
        if not self.is_playing:
            try:
                pygame.mixer.music.play()
                self.is_playing = True
                self.is_paused = False
            except:
                return False
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
        else:
            pygame.mixer.music.pause()
            self.is_paused = True
        
        return True
    
    def stop(self) -> None:
        """Stop the song."""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.position = 0.0
    
    def skip(self) -> None:
        """Skip the current song and trigger the song ending callback."""
        if self.is_playing:
            self.stop()
            # Trigger the song ending callback to handle queue management and next song
            if self.song_end_callback:
                self.song_end_callback()
    
    def update_position(self, delta_time: float = 1.0) -> None:
        """Update playback position."""
        if self.is_playing and not self.is_paused:
            self.position += delta_time
            
            # Check if song ended - pygame.mixer.music.get_busy() returns False when song finishes
            if not pygame.mixer.music.get_busy():
                self.is_playing = False
                self.is_paused = False
                self.position = 0.0
                
                # Notify the app that a song has ended
                if self.song_end_callback:
                    self.song_end_callback()
            # Also cap position at duration to prevent showing time beyond actual song length
            elif self.position > self.duration:
                self.position = self.duration
    
    def format_time(self, seconds: float) -> str:
        """Format time in MM:SS format."""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_time_display(self) -> str:
        """Get the time display string."""
        if not self.song_path:
            return "--:-- / --:--"
        current = self.format_time(self.position)
        total = self.format_time(self.duration)
        return f"{current} / {total}"


class SettingsScreen(ModalScreen[bool]):
    """Settings screen for editing playlist configurations and Spotify credentials."""
    
    CSS = """
    SettingsScreen {
        align: center middle;
    }
    
    #settings-container {
        width: auto;
        height: auto;
        min-width: 80;
        max-width: 120;
        background: $surface;
        border: solid $primary;
        padding: 2;
    }
    
    .title {
        color: $primary;
        text-align: center;
        margin-bottom: 2;
        text-style: bold;
    }
    
    .subtitle {
        color: $accent;
        margin-bottom: 1;
        margin-top: 1;
    }
    
    .json-editor {
        height: auto;
        min-height: 5;
        max-height: 20;
        margin-bottom: 2;
        border: solid $accent;
    }
    
    #action-buttons {
        height: auto;
        margin-top: 1;
    }
    
    .save-btn {
        background: $primary;
        color: $text;
        margin-right: 1;
        min-width: 12;
        max-width: 20;
    }
    
    .close-btn {
        background: $surface-lighten-1;
        color: $text;
        min-width: 12;
        max-width: 20;
    }
    """
    
    def __init__(self, settings: PlaylistSettings):
        super().__init__()
        self.settings = settings
        self.original_playlists_json = ""
        self.original_spotify_json = ""

    def compose(self) -> ComposeResult:
        with Container(id="settings-container"):
            yield Label("Settings", classes="title")
            
            yield Label("Playlists", classes="subtitle")
            yield TextArea(id="playlists-editor", language="json", theme="monokai", classes="json-editor")
            
            yield Label("Spotify API Credentials", classes="subtitle")
            yield TextArea(id="spotify-editor", language="json", theme="monokai", classes="json-editor")
            
            with Horizontal(id="action-buttons"):
                yield Button("Save", id="save-btn", classes="save-btn")
                yield Button("Close", id="close-btn", classes="close-btn")
    
    def on_mount(self) -> None:
        """Initialize the settings screen with current JSON."""
        self._load_json_content()
        # Focus the first text area
        self.query_one("#playlists-editor", TextArea).focus()

    def _load_json_content(self) -> None:
        """Load the current settings as formatted JSON."""
        try:
            # Load playlists data
            playlists_data = self.settings.get_all_playlists()
            playlists_json = json.dumps(playlists_data, indent=2)
            self.original_playlists_json = playlists_json
            
            # Load Spotify credentials data
            spotify_data = self.settings.get_spotify_credentials()
            spotify_json = json.dumps(spotify_data, indent=2)
            self.original_spotify_json = spotify_json
            
            # Set the content in the text areas
            playlists_area = self.query_one("#playlists-editor", TextArea)
            playlists_area.text = playlists_json
            
            spotify_area = self.query_one("#spotify-editor", TextArea)
            spotify_area.text = spotify_json
            
        except Exception as e:
            print(f"Error loading settings: {str(e)}")
    
    def _validate_and_save_settings(self) -> bool:
        """Validate and save both JSON editors' content."""
        try:
            # Get content from both editors
            playlists_area = self.query_one("#playlists-editor", TextArea)
            spotify_area = self.query_one("#spotify-editor", TextArea)
            
            playlists_content = playlists_area.text
            spotify_content = spotify_area.text
            
            # Parse and validate playlists JSON
            playlists_parsed = json.loads(playlists_content)
            if not isinstance(playlists_parsed, dict):
                raise ValueError("Playlists must be an object")
            
            # Validate each playlist
            for name, config in playlists_parsed.items():
                if not isinstance(config, dict):
                    raise ValueError(f"Playlist '{name}' must be an object")
                if 'url' not in config or 'directory' not in config:
                    raise ValueError(f"Playlist '{name}' must have 'url' and 'directory' fields")
                if not isinstance(config['url'], str) or not isinstance(config['directory'], str):
                    raise ValueError(f"Playlist '{name}' url and directory must be strings")
            
            # Parse and validate Spotify credentials JSON
            spotify_parsed = json.loads(spotify_content)
            if not isinstance(spotify_parsed, dict):
                raise ValueError("Spotify credentials must be an object")
            
            # Update settings with new data
            self.settings.playlists = playlists_parsed
            self.settings.save_settings()
            
            self.settings.spotify_credentials = spotify_parsed
            self.settings.save_spotify_credentials()
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {str(e)}")
            return False
        except ValueError as e:
            print(f"Invalid structure: {str(e)}")
            return False
        except Exception as e:
            print(f"Error saving: {str(e)}")
            return False
    
    # Removed real-time validation for cleaner UI
    
    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            if self._validate_and_save_settings():
                self.dismiss(True)
        elif event.button.id == "close-btn":
            self.dismiss(False)
    
    def on_key(self, event) -> None:
        """Handle key presses."""
        if event.key == "ctrl+c":
                self.dismiss(False)
        if event.key == "escape":
            self.dismiss(False)
            event.stop()  # Prevent event from propagating
        # Allow all other keys to be handled by TextArea widgets for proper text editing
        # Only intercept specific keys that need special handling


class CommandPrompt(ModalScreen[tuple[str, str]]):
    """Command prompt modal for searching playlists and songs."""
    
    CSS = """
    CommandPrompt {
        align: center middle;
    }
    
    #command-container {
        width: 60%;
        height: 50%;
        background: $surface;
        border: solid $primary;
        padding: 1;
    }
    
    #command-input {
        height: 3;
        margin-bottom: 1;
    }
    
    #results-list {
        height: 1fr;
    }
    """
    
    def __init__(self, playlists: List[str], all_songs: dict[str, List[str]], app_instance=None):
        super().__init__()
        self.playlists = playlists
        self.all_songs = all_songs  # playlist_name -> list of song paths
        self.current_query = ""
        self.results: List[tuple[str, str, str]] = []  # (display_text, type, path)
        self.app_instance = app_instance  # Reference to main app for queue operations
    
    def compose(self) -> ComposeResult:
        with Container(id="command-container"):
            yield Input(placeholder="Search playlists, songs, and screens...", id="command-input")
            yield ListView(id="results-list")
    
    def on_mount(self) -> None:
        """Focus the input when the modal opens."""
        self.query_one("#command-input", Input).focus()
        self._update_results("")
    
    def _parse_filename(self, filepath: str) -> tuple[str, str]:
        """Parse filename using improved parsing function that handles various formats."""
        return parse_music_filename(filepath)
    
    def _update_results(self, query: str) -> None:
        """Update the results list based on the search query."""
        self.current_query = query.lower()
        self.results = []
        
        if not self.current_query:
            # Show special commands, queue, download screen and all playlists when no query
            self.results.append(("\\[+] Shuffle Playlist", "shuffle", "shuffle"))
            self.results.append(("\\[+] Shuffle All Songs", "shuffle_all", "shuffle_all"))
            self.results.append(("\\[+] Settings", "settings", "settings"))
            self.results.append(("\\[+] Queue", "queue", "queue"))
            self.results.append(("\\[+] Download Playlist", "download_playlist", "download_playlist"))
            self.results.append(("\\[+] Download All Playlists", "download_all", "download_all"))
            self.results.append(("\\[+] Download Status", "download", "download"))
            for playlist in self.playlists:
                self.results.append((f"\\[=] {playlist}", "playlist", playlist))
        else:
            # Check for special commands (searchable by various terms including "+", or "[+]")
            special_commands_searchable = ["shuffle", "settings", "queue", "download", "logs", "+", "[+]", "cmd", "all"]
            if any(term in self.current_query for term in special_commands_searchable):
                # Add specific matches based on search terms
                if any(term in self.current_query for term in ["shuffle", "+", "[+]", "random"]):
                    self.results.append(("\\[+] Shuffle Playlist", "shuffle", "shuffle"))
                    if any(term in self.current_query for term in ["all", "everything"]):
                        self.results.append(("\\[+] Shuffle All Songs", "shuffle_all", "shuffle_all"))
                if any(term in self.current_query for term in ["shuffle", "all", "everything"]):
                    self.results.append(("\\[+] Shuffle All Songs", "shuffle_all", "shuffle_all"))
                if any(term in self.current_query for term in ["settings", "+", "[+]", "cmd"]):
                    self.results.append(("\\[+] Settings", "settings", "settings"))
                if any(term in self.current_query for term in ["queue", "+", "[+]", "q"]):
                    self.results.append(("\\[+] Queue", "queue", "queue"))
                if any(term in self.current_query for term in ["download", "+", "[+]", "d"]):
                    self.results.append(("\\[+] Download Playlist", "download_playlist", "download_playlist"))
                    self.results.append(("\\[+] Download Status", "download", "download"))
                    if any(term in self.current_query for term in ["all", "everything"]):
                        self.results.append(("\\[+] Download All Playlists", "download_all", "download_all"))
                if any(term in self.current_query for term in ["download", "all", "everything"]):
                    self.results.append(("\\[+] Download All Playlists", "download_all", "download_all"))
            
            # Search across playlists and songs
            playlist_matches = []
            song_matches = []
            
            # Search playlists (searchable by name, "=", or "[=]")
            for playlist in self.playlists:
                playlist_searchable = f"= [=] {playlist}".lower()
                if self.current_query in playlist_searchable:
                    playlist_matches.append((f"\\[=] {playlist}", "playlist", playlist))
            
            # Search songs across all playlists (searchable by content)
            for playlist_name, songs in self.all_songs.items():
                for song_path in songs:
                    song, artist = self._parse_filename(song_path)
                    searchable_text = f"{song} {artist} {os.path.basename(song_path)}".lower()
                    if self.current_query in searchable_text:
                        display_text = f"{song} by {artist} (in {playlist_name})"
                        song_matches.append((display_text, "song", song_path))
            
            # Combine results, prioritize settings/commands, then playlists, then songs, limit to top 20
            self.results = (self.results + playlist_matches + song_matches)[:20]
        
        # Update the ListView
        results_list = self.query_one("#results-list", ListView)
        results_list.clear()
        
        for display_text, result_type, path in self.results:
            results_list.append(ListItem(Label(display_text)))
        
        # Select first item if available
        if self.results:
            try:
                results_list.index = 0
            except AttributeError:
                # If index is read-only, try alternative method
                results_list.highlighted_child = 0
    
    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "command-input":
            self._update_results(event.value)
    
    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle enter key in input."""
        if event.input.id == "command-input":
            self._select_current_result()
    
    @on(ListView.Selected)
    def on_list_selected(self, event: ListView.Selected) -> None:
        """Handle list item selection."""
        self._select_current_result()
    
    def _select_current_result(self) -> None:
        """Select the currently highlighted result."""
        results_list = self.query_one("#results-list", ListView)
        if results_list.index is not None and results_list.index < len(self.results):
            display_text, result_type, path = self.results[results_list.index]
            self.dismiss((result_type, path))
    
    def _add_current_result_to_queue(self) -> None:
        """Add currently highlighted song to queue without closing prompt."""
        results_list = self.query_one("#results-list", ListView)
        if results_list.index is not None and results_list.index < len(self.results):
            display_text, result_type, path = self.results[results_list.index]
            
            # Only handle songs for queue addition
            if result_type == "song" and self.app_instance:
                self.app_instance._add_song_to_queue(path)
                # Optionally provide visual feedback that song was added
                # Could update the display text temporarily, but keeping it simple for now
    
    def on_key(self, event) -> None:
        """Handle key presses in the command prompt."""
        if event.key == "ctrl+c":
            if self.app_instance:
                self.app_instance.exit()
            else:
                self.dismiss(None)
        if event.key == "escape":
            self.dismiss(None)
            event.stop()  # Prevent event from propagating
        elif event.key == "enter":
            # Handle Enter key to select current result
            self._select_current_result()
            event.stop()  # Prevent event from propagating
        elif event.key == "shift+enter":
            # Handle Shift+Enter key to add song to queue
            self._add_current_result_to_queue()
            event.stop()  # Prevent event from propagating
        elif event.key in ["up", "down"]:
            # Handle up/down navigation manually
            results_list = self.query_one("#results-list", ListView)
            current_index = results_list.index if results_list.index is not None else 0
            
            if event.key == "up" and current_index > 0:
                new_index = current_index - 1
            elif event.key == "down" and current_index < len(self.results) - 1:
                new_index = current_index + 1
            else:
                return  # No change needed
            
            # Try to set the new index
            try:
                results_list.index = new_index
            except AttributeError:
                # If index is read-only, prevent default and let Textual handle it
                pass
            
            event.stop()  # Prevent event from propagating


class QueueScreen(ModalScreen[bool]):
    """Queue view screen showing current playback queue."""
    
    CSS = """
    QueueScreen {
        align: center middle;
    }
    
    #queue-container {
        width: 80%;
        height: 80%;
        background: $surface;
        border: solid $primary;
        padding: 1;
    }
    
    #queue-title {
        color: $primary;
        text-style: bold;
        margin-bottom: 1;
        text-align: center;
    }
    
    #queue-table {
        height: 1fr;
        margin-bottom: 1;
        width: 100%;
        max-width: 100%;
    }
    
    #queue-info {
        color: $accent;
        text-align: center;
        margin-bottom: 1;
    }
    """
    
    def __init__(self, app_instance):
        super().__init__()
        self.app_instance = app_instance
        self.selected_song_index: Optional[int] = None  # Index of currently selected song for swapping
    
    def compose(self) -> ComposeResult:
        with Container(id="queue-container"):
            yield Label(" Queue", id="queue-title")
            yield Label("", id="queue-info")
            yield DataTable(id="queue-table")
    
    def on_mount(self) -> None:
        """Initialize the queue screen."""
        self._update_queue_display()
    
    def _parse_filename(self, filepath: str) -> tuple[str, str]:
        """Parse filename using improved parsing function that handles various formats."""
        return parse_music_filename(filepath)
    
    def _update_queue_display(self) -> None:
        """Update the queue display with current queue contents."""
        queue_table = self.query_one("#queue-table", DataTable)
        queue_info = self.query_one("#queue-info", Label)
        
        # Save current cursor position
        current_cursor_row = queue_table.cursor_row
        
        # Clear and setup queue table
        queue_table.clear(columns=True)
        queue_table.add_column("", key="status", width=3)  # Current/User indicator (fixed width)
        queue_table.add_column("Song", key="song", width=40)  # Fixed width for song column
        queue_table.add_column("Artist", key="artist", width=30)  # Fixed width for artist column
        
        queue_table.cursor_type = "row"
        queue_table.zebra_stripes = True
        
        if not self.app_instance.queue:
            queue_info.update("No songs in queue")
            return
        
        # Update info text
        total_songs = len(self.app_instance.queue)
        current_pos = self.app_instance.queue_position + 1
        info_text = f"Position {current_pos} of {total_songs} songs"
        
        if self.selected_song_index is not None:
            info_text += f" | Selected song at position {self.selected_song_index + 1}"
        
        queue_info.update(info_text)
        
        # Add queue rows
        for i, song_metadata in enumerate(self.app_instance.queue):
            song_path = song_metadata['path']
            is_user_added = song_metadata.get('user_added', False)
            song, artist = self._parse_filename(song_path)
            
            # Status indicator
            if i == self.app_instance.queue_position:
                status = "►"  # Currently playing
                status_style = "bold green"
            elif i == self.selected_song_index:
                status = "●"  # Selected for swapping
                status_style = "bold yellow"
            else:
                status = ""
                status_style = ""
            
            # Add row with appropriate styling
            if i == self.app_instance.queue_position:
                # Current song - highlight in green
                queue_table.add_row(
                    Text(status, style=status_style),
                    Text(song, style="bold green"),
                    Text(artist, style="bold green"),
                    key=str(i)
                )
            elif i == self.selected_song_index:
                # Selected song - highlight in yellow
                queue_table.add_row(
                    Text(status, style=status_style),
                    Text(song, style="bold yellow"),
                    Text(artist, style="bold yellow"),
                    key=str(i)
                )
            elif is_user_added:
                # User-added song - highlight in cyan
                queue_table.add_row(
                    Text(status, style=status_style),
                    Text(song, style="cyan"),
                    Text(artist, style="cyan"),
                    key=str(i)
                )
            else:
                # Regular playlist song
                queue_table.add_row(status, song, artist, key=str(i))
        
        # Restore cursor position, or move to current song if this is the first time
        if current_cursor_row is not None and current_cursor_row < len(self.app_instance.queue):
            # Restore previous cursor position
            queue_table.move_cursor(row=current_cursor_row)
        elif self.app_instance.queue_position < len(self.app_instance.queue):
            # Move to current song if no previous position (initial load)
            queue_table.move_cursor(row=self.app_instance.queue_position)
    
    def on_key(self, event) -> None:
        """Handle key presses."""
        if event.key == "ctrl+c":
            if self.app_instance:
                self.app_instance.exit()
            else:
                self.dismiss(False)
        if event.key == "escape" or event.key == "ctrl+shift+q":
            self.dismiss(False)
            event.stop()
        elif event.key == "enter":
            # Handle song selection and swapping
            queue_table = self.query_one("#queue-table", DataTable)
            if queue_table.cursor_row is not None and queue_table.cursor_row < len(self.app_instance.queue):
                cursor_pos = queue_table.cursor_row
                
                if self.selected_song_index is None:
                    # No song selected, select the current one
                    self.selected_song_index = cursor_pos
                    self._update_queue_display()
                elif self.selected_song_index == cursor_pos:
                    # Same song selected, deselect it
                    self.selected_song_index = None
                    self._update_queue_display()
                else:
                    # Different song selected, swap them
                    self._swap_songs(self.selected_song_index, cursor_pos)
                    self.selected_song_index = None  # Clear selection after swap
                    self._update_queue_display()
            event.stop()
        elif event.key == "delete" or event.key == "backspace":
            # Remove selected song from queue
            queue_table = self.query_one("#queue-table", DataTable)
            if queue_table.cursor_row is not None and queue_table.cursor_row < len(self.app_instance.queue):
                cursor_pos = queue_table.cursor_row
                
                # Don't remove if it's the currently playing song
                if cursor_pos != self.app_instance.queue_position:
                    # Clear selection if we're deleting the selected song
                    if self.selected_song_index == cursor_pos:
                        self.selected_song_index = None
                    elif self.selected_song_index is not None and cursor_pos < self.selected_song_index:
                        # Adjust selection index if we're deleting a song before it
                        self.selected_song_index -= 1
                    
                    # Remove the song
                    self.app_instance.queue.pop(cursor_pos)
                    
                    # Adjust queue position if needed
                    if cursor_pos < self.app_instance.queue_position:
                        self.app_instance.queue_position -= 1
                    
                    self._update_queue_display()
            event.stop()
        # Allow up/down navigation but stop other keys from propagating
        elif event.key not in ["up", "down", "pageup", "pagedown", "home", "end"]:
            event.stop()
    
    def _swap_songs(self, index1: int, index2: int) -> None:
        """Swap two songs in the queue."""
        if (0 <= index1 < len(self.app_instance.queue) and 
            0 <= index2 < len(self.app_instance.queue) and 
            index1 != index2):
            
            # Swap the songs
            queue = self.app_instance.queue
            queue[index1], queue[index2] = queue[index2], queue[index1]
            
            # Adjust queue position if needed
            current_pos = self.app_instance.queue_position
            if current_pos == index1:
                self.app_instance.queue_position = index2
            elif current_pos == index2:
                self.app_instance.queue_position = index1


class DownloadLogsScreen(ModalScreen[bool]):
    """Download logs screen showing logs from current or previous download."""
    
    CSS = """
    DownloadLogsScreen {
        align: center middle;
    }
    
    #download-container {
        width: 90%;
        height: 80%;
        background: $surface;
        border: solid $primary;
        padding: 1;
    }
    
    #playlist-title {
        color: magenta;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #output-area {
        height: 1fr;
        border: solid $accent;
        background: $surface-darken-1;
    }
    
    .output-text {
        color: $text;
    }
    """
    
    def __init__(self, playlist_name: str, logs: List[str], is_downloading: bool, app_instance=None):
        super().__init__()
        self.playlist_name = playlist_name
        self.logs = logs
        self.is_downloading = is_downloading
        self.app_instance = app_instance  # Reference to main app for live log updates
        self.refresh_timer = None
    
    def compose(self) -> ComposeResult:
        with Container(id="download-container"):
            # Get current status from app instance if available
            if self.app_instance and hasattr(self.app_instance, '_get_playlist_download_state'):
                try:
                    state = self.app_instance._get_playlist_download_state(self.playlist_name)
                    is_downloading = state['downloading']
                except:
                    is_downloading = self.is_downloading
            else:
                is_downloading = self.is_downloading
            
            status = "Downloading" if is_downloading else "Download Logs"
            yield Label(f"{status}: {self.playlist_name}", id="playlist-title")
            yield TextArea(id="output-area", read_only=True, classes="output-text")
    
    def on_mount(self) -> None:
        """Initialize the download logs screen."""
        # Always setup refresh timer to update logs (for live updates)
        self.refresh_timer = self.set_interval(0.5, self._refresh_output)
        
        # Display current logs and scroll to bottom initially
        self._refresh_output()
        
        # Ensure we start at the bottom
        self.call_after_refresh(self._scroll_to_bottom_initial)
    
    def _scroll_to_bottom_initial(self):
        """Scroll to bottom on initial load only if there are logs to show."""
        try:
            output_area = self.query_one("#output-area", TextArea)
            # Only scroll to bottom if there's actual content and it's not empty
            if output_area.text and output_area.text.strip() and "Download in progress" not in output_area.text:
                self._scroll_to_bottom_smooth(output_area)
        except:
            pass
    
    def _refresh_output(self):
        """Refresh the output display."""
        output_area = self.query_one("#output-area", TextArea)
        
        # Get fresh logs from app instance if available (playlist-specific)
        if self.app_instance and hasattr(self.app_instance, '_get_playlist_download_state'):
            try:
                state = self.app_instance._get_playlist_download_state(self.playlist_name)
                current_logs = state['logs']
                current_downloading = state['downloading']
            except:
                current_logs = self.logs
                current_downloading = self.is_downloading
        else:
            current_logs = self.logs
            current_downloading = self.is_downloading
        
        # Check if content has changed
        if current_logs:
            new_output_text = "\n".join(current_logs)
        else:
            if current_downloading:
                new_output_text = "Download in progress... Logs will appear here."
            else:
                new_output_text = "No download logs available. Use Ctrl+Shift+U to start a download."
        
        # Only update if content has actually changed
        current_text = output_area.text
        if current_text != new_output_text:
            # Save current scroll position and check if user was at bottom
            was_at_bottom = False
            current_scroll_y = 0
            max_scroll_y = 0
            
            try:
                # Get current scroll position for restoration
                if hasattr(output_area, 'scroll_y') and hasattr(output_area, 'max_scroll_y'):
                    current_scroll_y = getattr(output_area, 'scroll_y', 0)
                    max_scroll_y = getattr(output_area, 'max_scroll_y', 0)
                    # Consider "at bottom" if within 3 lines of the end (tighter tolerance)
                    was_at_bottom = (max_scroll_y - current_scroll_y) <= 3
                else:
                    # Assume at bottom for first load or if we can't determine position
                    was_at_bottom = True
            except:
                was_at_bottom = True
            
            # Check if this is just new content being appended (logs growing)
            is_incremental_update = (
                current_text and 
                new_output_text.startswith(current_text) and 
                len(new_output_text) > len(current_text)
            )
            
            if is_incremental_update and was_at_bottom:
                # For incremental updates when user was at bottom, 
                # try to append without full text replacement to avoid snap
                try:
                    # Get the new content to append
                    new_content = new_output_text[len(current_text):]
                    if new_content.startswith('\n'):
                        new_content = new_content[1:]  # Remove leading newline
                    
                    # Try to append the new content
                    if hasattr(output_area, 'append'):
                        output_area.append(new_content)
                    else:
                        # Fallback to full replacement but position cursor at end first
                        if hasattr(output_area, 'cursor_position'):
                            output_area.cursor_position = len(current_text)
                        output_area.text = new_output_text
                        
                        # Immediately scroll to bottom to minimize snap effect
                        self.call_after_refresh(lambda: self._scroll_to_bottom_smooth(output_area))
                        
                except Exception:
                    # If append fails, fall back to full replacement
                    output_area.text = new_output_text
                    if was_at_bottom:
                        self.call_after_refresh(lambda: self._scroll_to_bottom_smooth(output_area))
            else:
                # For non-incremental updates, preserve scroll position if user wasn't at bottom
                output_area.text = new_output_text
                
                if was_at_bottom:
                    # User was at bottom, scroll to new bottom
                    self.call_after_refresh(lambda: self._scroll_to_bottom_smooth(output_area))
                else:
                    # User was not at bottom, try to preserve relative position
                    self.call_after_refresh(lambda: self._restore_scroll_position(output_area, current_scroll_y))
    
    def _scroll_to_bottom_smooth(self, output_area):
        """Smoothly scroll to bottom of output area."""
        try:
            if hasattr(output_area, 'scroll_end'):
                output_area.scroll_end()
            elif hasattr(output_area, 'scroll_y') and hasattr(output_area, 'max_scroll_y'):
                output_area.scroll_y = output_area.max_scroll_y
        except:
            pass
    
    def _restore_scroll_position(self, output_area, target_scroll_y):
        """Restore scroll position to preserve user's reading location."""
        try:
            if hasattr(output_area, 'scroll_y') and hasattr(output_area, 'max_scroll_y'):
                # Ensure we don't scroll beyond the new max
                max_scroll = getattr(output_area, 'max_scroll_y', 0)
                restored_scroll = min(target_scroll_y, max_scroll)
                output_area.scroll_y = restored_scroll
        except:
            pass
    
    def on_key(self, event) -> None:
        """Handle key presses."""
        if event.key == "ctrl+c":
            self.exit()
        if event.key == "escape":
            if self.refresh_timer:
                self.refresh_timer.stop()
            self.dismiss(False)
            event.stop()
        elif event.key == "ctrl+shift+u":
            # Start download for current playlist directly from modal
            if self.app_instance and hasattr(self.app_instance, '_start_current_playlist_download'):
                self.app_instance._start_current_playlist_download()
            event.stop()
        elif event.key in ["up", "down", "pageup", "pagedown", "home", "end"]:
            # Allow manual scrolling of the logs
            output_area = self.query_one("#output-area", TextArea)
            try:
                if event.key == "up":
                    output_area.action_cursor_up()
                elif event.key == "down":
                    output_area.action_cursor_down()
                elif event.key == "pageup":
                    output_area.action_page_up()
                elif event.key == "pagedown":
                    output_area.action_page_down()
                elif event.key == "home":
                    output_area.action_cursor_line_start()
                elif event.key == "end":
                    output_area.action_cursor_line_end()
            except:
                # If TextArea actions don't work, try scroll methods
                try:
                    if event.key == "up" and hasattr(output_area, 'scroll_up'):
                        output_area.scroll_up()
                    elif event.key == "down" and hasattr(output_area, 'scroll_down'):
                        output_area.scroll_down()
                    elif event.key == "pageup" and hasattr(output_area, 'scroll_page_up'):
                        output_area.scroll_page_up()
                    elif event.key == "pagedown" and hasattr(output_area, 'scroll_page_down'):
                        output_area.scroll_page_down()
                    elif event.key == "home" and hasattr(output_area, 'scroll_home'):
                        output_area.scroll_home()
                    elif event.key == "down" and hasattr(output_area, 'scroll_down'):
                        output_area.scroll_down()
                    elif event.key == "pageup" and hasattr(output_area, 'scroll_page_up'):
                        output_area.scroll_page_up()
                    elif event.key == "pagedown" and hasattr(output_area, 'scroll_page_down'):
                        output_area.scroll_page_down()
                    elif event.key == "home" and hasattr(output_area, 'scroll_home'):
                        output_area.scroll_home()
                    elif event.key == "end" and hasattr(output_area, 'scroll_end'):
                        output_area.scroll_end()
                except:
                    pass
            event.stop()
        # For all other keys, let them pass through (but don't propagate to main app)
        else:
            event.stop()


# Keep the old DownloadOutputScreen for backwards compatibility if needed
class DownloadOutputScreen(ModalScreen[bool]):
    """Download output screen showing streaming output of current download."""
    
    CSS = """
    DownloadOutputScreen {
        align: center middle;
    }
    
    #download-container {
        width: 90%;
        height: 80%;
        background: $surface;
        border: solid $primary;
        padding: 1;
    }
    
    #playlist-title {
        color: magenta;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #output-area {
        height: 1fr;
        border: solid $accent;
        background: $surface-darken-1;
    }
    
    .output-text {
        color: $text;
    }
    """
    
    def __init__(self, playlist_name: str):
        super().__init__()
        self.playlist_name = playlist_name
        self.output_lines = []
        self.refresh_timer = None
    
    def compose(self) -> ComposeResult:
        with Container(id="download-container"):
            yield Label(f"Downloading: {self.playlist_name}", id="playlist-title")
            yield TextArea(id="output-area", read_only=True, classes="output-text")
    
    def on_mount(self) -> None:
        """Initialize the download output screen."""
        # Setup refresh timer to update output
        self.refresh_timer = self.set_interval(0.5, self._refresh_output)
        self._add_output_line("Starting download...")
        
        # Start the download in a separate thread
        def download_async():
            try:
                def progress_callback(current: int, total: int, message: str):
                    # Add progress messages to output
                    if total > 0:
                        self._add_output_line(f"[{current}/{total}] {message}")
                    else:
                        self._add_output_line(message)
                
                # Call our download function
                success = download_playlist(
                    self.playlist_name,
                    progress_callback=progress_callback
                )
                
                if success:
                    self._add_output_line("Download completed successfully!")
                else:
                    self._add_output_line("Download failed!")
                
            except Exception as e:
                self._add_output_line(f"Error: {str(e)}")
        
        # Start download in separate thread
        download_thread = threading.Thread(target=download_async)
        download_thread.daemon = True
        download_thread.start()
    
    def _add_output_line(self, line: str):
        """Add a line to the output buffer."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_lines.append(f"[{timestamp}] {line}")
        # Keep only last 100 lines
        if len(self.output_lines) > 100:
            self.output_lines = self.output_lines[-100:]
    
    def _refresh_output(self):
        """Refresh the output display."""
        output_area = self.query_one("#output-area", TextArea)
        
        # Create new output text
        new_output_text = "\n".join(self.output_lines)
        current_text = output_area.text
        
        # Only update if content has actually changed
        if current_text != new_output_text:
            # Check if we were at the bottom before the update
            was_at_bottom = False
            current_scroll_y = 0
            
            try:
                if hasattr(output_area, 'scroll_y') and hasattr(output_area, 'max_scroll_y'):
                    current_scroll_y = getattr(output_area, 'scroll_y', 0)
                    max_scroll = getattr(output_area, 'max_scroll_y', 0)
                    # Consider "at bottom" if within 3 lines of the end
                    was_at_bottom = (max_scroll - current_scroll_y) <= 3
                else:
                    # Default to scrolling to bottom if we can't determine position
                    was_at_bottom = True
            except:
                was_at_bottom = True
            
            # Check if this is just new content being appended
            is_incremental_update = (
                current_text and 
                new_output_text.startswith(current_text) and 
                len(new_output_text) > len(current_text)
            )
            
            if is_incremental_update and was_at_bottom:
                # For incremental updates when user was at bottom, try to append
                try:
                    new_content = new_output_text[len(current_text):]
                    if new_content.startswith('\n'):
                        new_content = new_content[1:]
                    
                    if hasattr(output_area, 'append'):
                        output_area.append(new_content)
                    else:
                        output_area.text = new_output_text
                        self.call_after_refresh(lambda: self._scroll_to_bottom_smooth(output_area))
                except Exception:
                    output_area.text = new_output_text
                    if was_at_bottom:
                        self.call_after_refresh(lambda: self._scroll_to_bottom_smooth(output_area))
            else:
                # Update content
                output_area.text = new_output_text
                
                if was_at_bottom:
                    # Auto-scroll to bottom if we were already at the bottom
                    self.call_after_refresh(lambda: self._scroll_to_bottom_smooth(output_area))
                else:
                    # Preserve scroll position if user wasn't at bottom
                    self.call_after_refresh(lambda: self._restore_scroll_position(output_area, current_scroll_y))
    
    def _scroll_to_bottom_smooth(self, output_area):
        """Smoothly scroll to bottom of output area."""
        try:
            if hasattr(output_area, 'scroll_end'):
                output_area.scroll_end()
            elif hasattr(output_area, 'scroll_y') and hasattr(output_area, 'max_scroll_y'):
                output_area.scroll_y = output_area.max_scroll_y
        except:
            pass
    
    def _restore_scroll_position(self, output_area, target_scroll_y):
        """Restore scroll position to preserve user's reading location."""
        try:
            if hasattr(output_area, 'scroll_y') and hasattr(output_area, 'max_scroll_y'):
                max_scroll = getattr(output_area, 'max_scroll_y', 0)
                restored_scroll = min(target_scroll_y, max_scroll)
                output_area.scroll_y = restored_scroll
        except:
            pass
    
    def on_key(self, event) -> None:
        """Handle key presses."""
        if event.key == "ctrl+c":
            self.exit()
        if event.key == "escape":
            if self.refresh_timer:
                self.refresh_timer.stop()
            self.dismiss(False)
            event.stop()


class MusicPlayerApp(App[None]):
    """Textual music player application."""
    
    def _parse_filename(self, filepath: str) -> tuple[str, str]:
        """Parse filename using improved parsing function that handles various formats."""
        return parse_music_filename(filepath)
    
    def _format_song_display(self, song: str, artist: str) -> str:
        """Format song and artist for display as '[song] by [artist]'."""
        return f"{song} by {artist}"
    
    def _get_song_duration(self, filepath: str) -> str:
        """Get song duration in MM:SS format using audio metadata."""
        try:
            # Try to get accurate duration from audio metadata
            audio_file = MutagenFile(filepath)
            if audio_file is not None and hasattr(audio_file, 'info') and hasattr(audio_file.info, 'length'):
                duration_seconds = audio_file.info.length
            else:
                # Fallback to file size estimation
                file_size = os.path.getsize(filepath)
                duration_seconds = file_size / (128 * 1024 / 8)
            
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            return f"{minutes:02d}:{seconds:02d}"
        except:
            return "00:00"
    
    def _get_download_date(self, filepath: str) -> str:
        """Get file creation/modification date in mm/dd/yy format."""
        try:
            # Use the earlier of creation time or modification time
            stat = os.stat(filepath)
            timestamp = min(stat.st_ctime, stat.st_mtime)
            date = datetime.fromtimestamp(timestamp)
            return date.strftime("%m/%d/%y")
        except:
            return "00/00/00"
    
    def _get_current_song_index(self) -> int:
        """Get the current song's index in the songs list, or -1 if not found."""
        if not self.current_song_path or not self.songs:
            return -1
        try:
            return self.songs.index(self.current_song_path)
        except ValueError:
            return -1
    
    def _get_current_song_display_index(self) -> int:
        """Get the current song's display index in the sorted table, or -1 if not found."""
        current_index = self._get_current_song_index()
        if current_index == -1:
            return -1
        try:
            return self.sorted_indices.index(current_index)
        except ValueError:
            return -1
    
    def _move_cursor_to_current_song(self) -> None:
        """Move the table cursor to the currently playing song if it exists in the current playlist."""
        display_index = self._get_current_song_display_index()
        if display_index >= 0:
            songs_table = self.query_one("#content-table", DataTable)
            songs_table.move_cursor(row=display_index)
    
    def _get_current_song_display(self) -> str:
        """Get current song name in 'song by artist' format for display."""
        if self.player.song_path:
            song, artist = self._parse_filename(self.player.song_path)
            return f"{song} by {artist}"
        else:
            return "No song playing"
    
    def _get_current_playlist_display(self) -> str:
        """Get current playlist name for display in the playlist area."""
        if self.current_playlist:
            return self.current_playlist
        else:
            return "No playlist selected"
    
    def _get_download_status_display(self) -> str:
        """Get download status for the current playlist."""
        if not self.current_playlist:
            return ""
        
        state = self._get_playlist_download_state(self.current_playlist)
        
        # Show active download status or last status
        if state['downloading']:
            return "Updating..."
        elif state['status']:
            return state['status']
        else:
            return ""
    
    def _page_up(self) -> None:
        """Navigate one page up in the songs table."""
        table = self.query_one("#content-table", DataTable)
        if table.cursor_row > 0:
            # Move up by 10 items (page size)
            new_row = max(0, table.cursor_row - 10)
            table.move_cursor(row=new_row)
    
    def _page_down(self) -> None:
        """Navigate one page down in the songs table."""
        table = self.query_one("#content-table", DataTable)
        max_row = len(self.sorted_indices) - 1
        if max_row >= 0 and table.cursor_row < max_row:
            # Move down by 10 items (page size)
            new_row = min(max_row, table.cursor_row + 10)
            table.move_cursor(row=new_row)
    
    def _move_to_top(self) -> None:
        """Move cursor to the top of the playlist."""
        table = self.query_one("#content-table", DataTable)
        if len(self.sorted_indices) > 0:
            table.move_cursor(row=0)
    
    def _move_to_bottom(self) -> None:
        """Move cursor to the bottom of the playlist."""
        table = self.query_one("#content-table", DataTable)
        max_row = len(self.sorted_indices) - 1
        if max_row >= 0:
            table.move_cursor(row=max_row)
    
    def _generate_queue_from_current_view(self, start_song_path: str) -> None:
        """Generate an infinite queue (10x playlist length) based on current view order."""
        if not self.songs or not self.sorted_indices:
            self.queue = []
            self.queue_position = 0
            return
        
        # Find the starting song's position in the current sorted view
        try:
            start_original_index = self.songs.index(start_song_path)
            start_display_index = self.sorted_indices.index(start_original_index)
        except ValueError:
            # Song not found in current view, start from beginning
            start_display_index = 0
        
        # Create the queue by repeating the current view order 10 times
        view_order = [self.songs[i] for i in self.sorted_indices]
        queue_length = len(view_order) * self._queue_generation_multiplier
        
        # Generate the queue starting from the selected song
        self.queue = []
        for i in range(queue_length):
            queue_index = (start_display_index + i) % len(view_order)
            song_path = view_order[queue_index]
            # Create song metadata object
            song_metadata = {
                'path': song_path,
                'user_added': False  # Songs from playlist generation are not user-added
            }
            self.queue.append(song_metadata)
        
        # Store the original playlist and order for reference
        self.queue_original_playlist = self.current_playlist
        self.queue_original_order = self.sorted_indices.copy()
        self.queue_position = 0
    
    def _add_song_to_queue(self, song_path: str) -> None:
        """Add a song after the last user-added song in the queue."""
        if not self.queue:
            # If no queue exists, generate one from current song
            if self.current_song_path:
                self._generate_queue_from_current_view(self.current_song_path)
            else:
                return
        
        # Create song metadata object for user-added song
        song_metadata = {
            'path': song_path,
            'user_added': True  # This song was added by the user
        }
        
        # Find the position after the last user-added song
        insert_position = self.queue_position + 1  # Default: after current position
        
        # Look for the last user-added song starting from current position
        for i in range(self.queue_position + 1, len(self.queue)):
            if self.queue[i].get('user_added', False):
                insert_position = i + 1  # Insert after this user-added song
            else:
                # Found first non-user-added song, stop searching
                break
        
        self.queue.insert(insert_position, song_metadata)
    
    def _get_next_song_from_queue(self) -> Optional[str]:
        """Get the next song from the queue."""
        if not self.queue:
            return None
        
        self.queue_position += 1
        if self.queue_position >= len(self.queue):
            # Extend queue if we've reached the end (infinite queue)
            self._extend_queue()
        
        if self.queue_position < len(self.queue):
            return self.queue[self.queue_position]['path']
        return None
    
    def _get_previous_song_from_queue(self) -> Optional[str]:
        """Get the previous song from the queue."""
        if not self.queue:
            return None
        
        if self.queue_position <= 0:
            # Already at the beginning, stay at position 0
            self.queue_position = 0
            return self.queue[0]['path']
        
        self.queue_position -= 1
        return self.queue[self.queue_position]['path']
    
    def _extend_queue(self) -> None:
        """Extend the queue by repeating the original order."""
        if not self.queue_original_order or not self.queue_original_playlist:
            return
        
        # Get the original playlist songs
        if self.queue_original_playlist != self.current_playlist:
            # Original playlist is different, use stored order
            playlist_config = self.settings.get_playlist(self.queue_original_playlist)
            if not playlist_config:
                return
            
            playlist_path = os.path.expanduser(playlist_config["directory"])
            if not os.path.exists(playlist_path):
                return
            
            # Load songs from original playlist
            audio_extensions = ['*.mp3', '*.flac', '*.wav', '*.m4a', '*.ogg', '*.aac']
            original_songs = []
            for ext in audio_extensions:
                pattern = os.path.join(playlist_path, ext)
                original_songs.extend(glob.glob(pattern))
                pattern = os.path.join(playlist_path, '**', ext)
                original_songs.extend(glob.glob(pattern, recursive=True))
            original_songs = sorted(list(set(original_songs)))
        else:
            # Same playlist, use current songs
            original_songs = self.songs
        
        # Extend queue with original order
        view_order = [original_songs[i] for i in self.queue_original_order if i < len(original_songs)]
        extension_length = len(view_order) * 2  # Add 2 more cycles
        
        for i in range(extension_length):
            queue_index = i % len(view_order)
            if queue_index < len(view_order):
                song_path = view_order[queue_index]
                # Create song metadata object for extended queue songs
                song_metadata = {
                    'path': song_path,
                    'user_added': False  # Extended songs are not user-added
                }
                self.queue.append(song_metadata)
    
    def _shuffle_playlist(self) -> None:
        """Generate a shuffled queue with fair distribution (10x playlist length)."""
        if not self.songs:
            return
        
        # Use current song as starting point if available, otherwise use first song
        current_song_path = self.current_song_path
        if not current_song_path and self.songs:
            # No current song, use the first song in current view order
            current_song_path = self.songs[self.sorted_indices[0]] if self.sorted_indices else self.songs[0]
        
        # Create a fair shuffle: ensure each song appears once before any song appears twice
        original_playlist_songs = self.songs.copy()
        queue_length = len(original_playlist_songs) * self._queue_generation_multiplier
        
        # Generate the shuffled queue using fair distribution
        self.queue = []
        songs_pool = original_playlist_songs.copy()
        
        # If we have a current song, start with it
        if current_song_path and current_song_path in songs_pool:
            self.queue.append({
                'path': current_song_path,
                'user_added': False
            })
            songs_pool.remove(current_song_path)
        
        # Fill the rest of the queue with fair shuffling
        while len(self.queue) < queue_length:
            if not songs_pool:
                # Refill the pool when empty (all songs have been used equally)
                songs_pool = original_playlist_songs.copy()
                # Remove current song if it was just added to avoid immediate repetition
                if self.queue and self.queue[-1]['path'] in songs_pool:
                    songs_pool.remove(self.queue[-1]['path'])
            
            if songs_pool:
                # Randomly select next song from available pool
                selected_song = random.choice(songs_pool)
                self.queue.append({
                    'path': selected_song,
                    'user_added': False
                })
                songs_pool.remove(selected_song)
        
        # Update queue metadata
        self.queue_original_playlist = self.current_playlist
        self.queue_original_order = list(range(len(original_playlist_songs)))  # Will be shuffled
        self.queue_position = 0
        
        # Start playing the first song in the shuffled queue if not already playing
        if self.queue and (not self.player.is_playing or not current_song_path):
            first_song = self.queue[0]['path']
            self.current_song_path = first_song
            self.player.load_and_play(first_song)
            self._refresh_table_highlighting()
    
    def _shuffle_all_songs(self) -> None:
        """Generate a shuffled queue from all songs across all playlists."""
        if not self.all_songs:
            return
        
        # Collect all songs from all playlists
        all_songs_list = []
        for playlist_name, playlist_songs in self.all_songs.items():
            all_songs_list.extend(playlist_songs)
        
        if not all_songs_list:
            return
        
        # Use current song as starting point if available
        current_song_path = self.current_song_path
        if not current_song_path and all_songs_list:
            # No current song, use the first song from all songs
            current_song_path = all_songs_list[0]
        
        # Create a fair shuffle: ensure each song appears once before any song appears twice
        queue_length = len(all_songs_list) * self._queue_generation_multiplier
        
        # Generate the shuffled queue using fair distribution
        self.queue = []
        songs_pool = all_songs_list.copy()
        
        # If we have a current song, start with it
        if current_song_path and current_song_path in songs_pool:
            self.queue.append({
                'path': current_song_path,
                'user_added': False
            })
            songs_pool.remove(current_song_path)
        
        # Fill the rest of the queue with fair shuffling
        while len(self.queue) < queue_length:
            if not songs_pool:
                # Refill the pool when empty (all songs have been used equally)
                songs_pool = all_songs_list.copy()
                # Remove current song if it was just added to avoid immediate repetition
                if self.queue and self.queue[-1]['path'] in songs_pool:
                    songs_pool.remove(self.queue[-1]['path'])
            
            if songs_pool:
                # Randomly select next song from available pool
                selected_song = random.choice(songs_pool)
                self.queue.append({
                    'path': selected_song,
                    'user_added': False
                })
                songs_pool.remove(selected_song)
        
        # Update queue metadata - set to "All Songs" mode
        self.queue_original_playlist = "All Songs"
        self.queue_original_order = list(range(len(all_songs_list)))
        self.queue_position = 0
        
        # Start playing the first song in the shuffled queue if not already playing
        if self.queue and (not self.player.is_playing or not current_song_path):
            first_song = self.queue[0]['path']
            self.current_song_path = first_song
            self.player.load_and_play(first_song)
            self._refresh_table_highlighting()
        
        # Update display to show we're in "All Songs" shuffle mode
        # Toast notification removed
    
    def _on_song_ended(self) -> None:
        """Handle when a song finishes playing."""
        # Check if the current song in the queue was user-added
        current_song_was_user_added = False
        if self.queue and self.queue_position < len(self.queue):
            current_song_was_user_added = self.queue[self.queue_position].get('user_added', False)
        
        # If current song was user-added, remove it from the queue
        if current_song_was_user_added and self.queue and self.queue_position < len(self.queue):
            self.queue.pop(self.queue_position)
            # Adjust position since we removed the current song
            self.queue_position -= 1
        
        # Automatically play the next song
        self._next_song()
    
    def _play_song_and_generate_queue(self, song_path: str) -> None:
        """Play a song and generate a new queue from current view."""
        self.current_song_path = song_path
        self.player.load_and_play(song_path)
        self._generate_queue_from_current_view(song_path)
        self._refresh_table_highlighting()
    
    def _skip_song(self) -> None:
        """Skip the current song and trigger the song ending callback."""
        if self.player.is_playing:
            # Use the skip method which will trigger the song ending callback
            self.player.skip()
        else:
            # If not playing, just go to next song without callback
            self._next_song()
    
    def _next_song(self) -> None:
        """Play the next song from the queue."""
        if self.current_view == "songs" and self.songs:
            # Use queue-based navigation
            if not self.queue and self.current_song_path:
                # Generate queue if it doesn't exist
                self._generate_queue_from_current_view(self.current_song_path)
            
            next_song = self._get_next_song_from_queue()
            if next_song:
                self.current_song_path = next_song
                self.player.load_and_play(next_song)
                self._refresh_table_highlighting()
            elif self.songs:
                # Fallback to first song if queue fails
                if self.sorted_indices:
                    first_original_index = self.sorted_indices[0]
                    selected_song = self.songs[first_original_index]
                    self._play_song_and_generate_queue(selected_song)
    
    def _previous_or_reset_song(self) -> None:
        """Reset current song if <3 seconds, otherwise play previous song."""
        if self.current_view == "songs" and self.songs and self.current_song_path:
            if self.player.position < 3.0:
                # Less than 3 seconds, go to previous song from queue
                if not self.queue:
                    # Generate queue if it doesn't exist
                    self._generate_queue_from_current_view(self.current_song_path)
                
                prev_song = self._get_previous_song_from_queue()
                if prev_song:
                    self.current_song_path = prev_song
                    self.player.load_and_play(prev_song)
                    self._refresh_table_highlighting()
                # Note: No fallback to table view - if queue exists, stay within queue bounds
            else:
                # More than 3 seconds, restart current song
                if self.current_song_path:
                    self.player.load_and_play(self.current_song_path)
    
    CSS = """
    Screen {
        layout: vertical;
        border: none;
    }
    
    #main-content {
        height: 1fr;
    }
    
    #player-bar {
        height: 2;
        padding: 0 2 0 1;
        margin: 1 0 1 0;
    }
    
    #song-name {
        color: $warning;
        height: 1;
        padding: 0;
        margin: 0;
    }
    
    #time-display {
        color: #808080;
        height: 1;
        padding: 0;
        margin: 0;
    }
    
    #playlist-display {
        color: magenta;
        height: 1;
        padding: 0;
        margin: 0;
        text-align: right;
        width: 1fr;
    }
    
    #status-display {
        color: #808080;
        height: 1;
        padding: 0;
        margin: 0;
        text-align: right;
        width: 1fr;
    }
    
    DataTable {
        height: 1fr;
        width: 100%;
    }
    
    #content-table {
        height: 1fr;
        width: 100%;
    }
    
    DataTable > .datatable--cursor {
        background: blue;
        color: white;
    }
    
    DataTable:focus > .datatable--cursor {
        background: blue;
        color: white;
    }
    

    """
    
    def __init__(self):
        super().__init__()
        self.player = MusicPlayer()
        self.update_timer: Optional[Timer] = None
        self.current_view = "songs"  # Always start in songs view
        self.current_playlist: Optional[str] = None
        self.playlists: List[str] = []
        self.songs: List[str] = []
        self.all_songs: dict[str, List[str]] = {}  # playlist_name -> list of song paths
        self.current_song_path: Optional[str] = None  # Track current playing song by path
        self.last_click_time = 0.0
        self.last_click_index = -1
        
        # Modal state tracking
        self.modal_active = False
        
        # Sorting state
        self.sort_column: Optional[str] = None  # Column key being sorted
        self.sort_reverse: bool = False  # True for descending, False for ascending
        self.sorted_indices: List[int] = []  # Maps display row to original song index
        
        # Initialize settings and per-playlist download tracking
        self.settings = PlaylistSettings()
        
        # Per-playlist download tracking: playlist_name -> {logs: [], status: "", downloading: bool, thread: Thread}
        self._playlist_download_state = {}
        
        # Current playlist state (for quick access)
        self._download_logs = []
        self._download_status = ""
        
        # Track last highlighted song to avoid unnecessary refreshes
        self._last_highlighted_song = None
        
        # Queue system variables
        self.queue: List[Dict[str, Any]] = []  # Current playback queue (song metadata)
        self.queue_original_playlist: Optional[str] = None  # Playlist that generated the queue
        self.queue_original_order: List[int] = []  # Original order of songs when queue was generated
        self.queue_position: int = 0  # Current position in the queue
        self._queue_generation_multiplier = 10  # Generate 10x playlist length
        
        # Set up song end callback
        self.player.song_end_callback = self._on_song_ended
        
        # Initialize global hotkey manager
        self.global_hotkey_manager = GlobalHotkeyManager(self)
        
        # Load playlists and start with first playlist
        self._load_playlists()
        if self.playlists:
            self.current_playlist = self.playlists[0]
            self._set_current_playlist_state(self.current_playlist)  # Initialize download state
            self._load_songs(self.current_playlist)
    
    def _load_playlists(self) -> None:
        """Load all playlists from settings and preload all songs for search."""
        self.playlists = self.settings.get_playlist_names()
        
        # Preload all songs for search functionality
        self.all_songs = {}
        for playlist in self.playlists:
            playlist_config = self.settings.get_playlist(playlist)
            if playlist_config:
                playlist_path = os.path.expanduser(playlist_config["directory"])
                if os.path.exists(playlist_path):
                    # Common audio file extensions
                    audio_extensions = ['*.mp3', '*.flac', '*.wav', '*.m4a', '*.ogg', '*.aac']
                    
                    playlist_songs = []
                    for ext in audio_extensions:
                        pattern = os.path.join(playlist_path, ext)
                        playlist_songs.extend(glob.glob(pattern))
                        # Also check subdirectories
                        pattern = os.path.join(playlist_path, '**', ext)
                        playlist_songs.extend(glob.glob(pattern, recursive=True))
                    
                    # Remove duplicates and sort
                    self.all_songs[playlist] = sorted(list(set(playlist_songs)))
    
    def _load_songs(self, playlist_name: str) -> None:
        """Load all songs from a specific playlist."""
        playlist_config = self.settings.get_playlist(playlist_name)
        if not playlist_config:
            self.songs = []
            self.sorted_indices = []
            return
        
        playlist_path = os.path.expanduser(playlist_config["directory"])
        if not os.path.exists(playlist_path):
            self.songs = []
            self.sorted_indices = []
            return
        
        # Common audio file extensions
        audio_extensions = ['*.mp3', '*.flac', '*.wav', '*.m4a', '*.ogg', '*.aac']
        
        self.songs = []
        for ext in audio_extensions:
            pattern = os.path.join(playlist_path, ext)
            self.songs.extend(glob.glob(pattern))
            # Also check subdirectories
            pattern = os.path.join(playlist_path, '**', ext)
            self.songs.extend(glob.glob(pattern, recursive=True))
        
        # Remove duplicates and sort
        self.songs = sorted(list(set(self.songs)))
        
        # Set default sorting to date (oldest first)
        self.sort_column = "date"
        self.sort_reverse = False
        
        # Apply default sorting by date (oldest first)
        self._sort_songs("date")
    
    def _parse_duration_to_seconds(self, duration_str: str) -> int:
        """Convert MM:SS duration string to seconds for sorting."""
        try:
            parts = duration_str.split(':')
            if len(parts) == 2:
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            return 0
        except (ValueError, IndexError):
            return 0
    
    def _parse_date_to_timestamp(self, date_str: str) -> float:
        """Convert MM/DD/YY date string to timestamp for sorting."""
        try:
            # Parse date in MM/DD/YY format
            date_obj = datetime.strptime(date_str, "%m/%d/%y")
            return date_obj.timestamp()
        except ValueError:
            return 0.0
    
    def _sort_songs(self, column_key: str) -> None:
        """Sort songs by the specified column."""
        if not self.songs:
            return
        
        # Toggle sort direction if clicking the same column
        if self.sort_column == column_key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column_key
            self.sort_reverse = False
        
        # Create list of (sort_value, original_index) tuples
        sort_data = []
        
        for i, song_path in enumerate(self.songs):
            song, artist = self._parse_filename(song_path)
            
            if column_key == "song":
                sort_value = song.lower()
            elif column_key == "artist":
                sort_value = artist.lower()
            elif column_key == "duration":
                duration = self._get_song_duration(song_path)
                sort_value = self._parse_duration_to_seconds(duration)
            elif column_key == "date":
                date_downloaded = self._get_download_date(song_path)
                sort_value = self._parse_date_to_timestamp(date_downloaded)
            else:
                sort_value = ""
            
            sort_data.append((sort_value, i))
        
        # Sort the data
        sort_data.sort(key=lambda x: x[0], reverse=self.sort_reverse)
        
        # Update sorted indices
        self.sorted_indices = [item[1] for item in sort_data]
    
    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        with Vertical():
            with Vertical(id="main-content"):
                # Only show the songs table (no more playlists view)
                yield DataTable(id="content-table")
            yield Label("")  # Empty line for spacing
            with Vertical(id="player-bar"):
                # First line: Song name (left) | Playlist name (right)
                with Horizontal():
                    yield Label(self._get_current_song_display(), id="song-name")
                    yield Label(self._get_current_playlist_display(), id="playlist-display")
                # Second line: Time progress (left) | Download status (right)
                with Horizontal():
                    yield Label(self.player.get_time_display(), id="time-display")
                    yield Label(self._get_download_status_display(), id="status-display")
    
    def on_mount(self) -> None:
        """Initialize when app starts."""
        # Set up timer to update the display every 100ms for responsive highlighting
        self.update_timer = self.set_interval(0.1, self.update_display)
        
        # Start global hotkey manager for media keys
        self.global_hotkey_manager.start()
        
        # Populate initial playlist view
        self._update_list_view()
    
    def _get_column_header(self, column_key: str, title: str) -> str:
        """Get column header with sort indicator."""
        if self.sort_column == column_key:
            arrow = " ↓" if self.sort_reverse else " ↑"
            return title + arrow
        return title
    
    def _update_list_view(self) -> None:
        """Update the songs table view."""
        if self.current_playlist:
            songs_table = self.query_one("#content-table", DataTable)
            
            # Clear and setup songs table
            songs_table.clear(columns=True)
            songs_table.add_column(self._get_column_header("song", "Song Name"), key="song", width=50)
            songs_table.add_column(self._get_column_header("artist", "Artist Name"), key="artist", width=30)
            songs_table.add_column(self._get_column_header("duration", "Duration"), key="duration", width=10)
            songs_table.add_column(self._get_column_header("date", "Date Downloaded"), key="date", width=18)
            
            # Configure table behavior
            songs_table.cursor_type = "row"
            songs_table.zebra_stripes = True
            
            # Add song rows in sorted order (only if there are songs)
            if self.songs:
                for display_index, original_index in enumerate(self.sorted_indices):
                    song_path = self.songs[original_index]
                    song, artist = self._parse_filename(song_path)
                    duration = self._get_song_duration(song_path)
                    date_downloaded = self._get_download_date(song_path)
                    
                    # Check if this is the currently playing song
                    is_playing = (song_path == self.current_song_path and self.player.is_playing)
                    
                    if is_playing:
                        # Style the currently playing song with green background
                        song_styled = Text(song, style="bold orange1")
                        artist_styled = Text(artist, style="bold orange1")
                        duration_styled = Text(duration, style="bold orange1")
                        date_styled = Text(date_downloaded, style="bold orange1")
                        songs_table.add_row(song_styled, artist_styled, duration_styled, date_styled, key=str(original_index))
                    else:
                        songs_table.add_row(song, artist, duration, date_downloaded, key=str(original_index))
            # If no songs, the table will display with just headers and no rows
    

    
    def update_display(self) -> None:
        """Update the player display."""
        self.player.update_position(0.1)  # Update position by 0.1 seconds (our timer interval)
        
        # Update the time display
        time_widget = self.query_one("#time-display", Label)
        time_widget.update(self.player.get_time_display())
        
        # Update song name (now shows "song by artist")
        song_widget = self.query_one("#song-name", Label)
        song_widget.update(self._get_current_song_display())
        
        # Update playlist display (just playlist name)
        playlist_widget = self.query_one("#playlist-display", Label)
        playlist_widget.update(self._get_current_playlist_display())
        
        # Update download status display
        status_widget = self.query_one("#status-display", Label)
        status_widget.update(self._get_download_status_display())
        
        # Check if we need to update table highlighting (only when the highlighted song changes)
        current_highlighted = self.current_song_path if self.player.is_playing else None
        if current_highlighted != self._last_highlighted_song:
            self._last_highlighted_song = current_highlighted
            self._refresh_table_highlighting()
    
    def _refresh_table_highlighting(self) -> None:
        """Refresh the table to update highlighting for the currently playing song."""
        if self.current_view == "songs" and self.songs:
            # Save current cursor position and scroll state
            songs_table = self.query_one("#content-table", DataTable)
            current_cursor_row = songs_table.cursor_row
            current_scroll_y = getattr(songs_table, 'scroll_y', 0)
            
            # Update the table
            self._update_list_view()
            
            # Restore cursor position
            if current_cursor_row is not None and current_cursor_row < len(self.sorted_indices):
                songs_table.move_cursor(row=current_cursor_row)
            
            # Restore scroll position
            try:
                if hasattr(songs_table, 'scroll_y'):
                    songs_table.scroll_y = current_scroll_y
            except:
                pass  # Ignore any errors restoring scroll position
    
    def on_key(self, event) -> None:
        """Handle key presses."""
        # Debug: print the key to see what's being detected
        print(f"Key pressed: '{event.key}' - Modal active: {self.modal_active}")
        
        # If a modal is active, don't process most keys (except for essential ones like ctrl+c)
        if self.modal_active:
            if event.key == "ctrl+c":
                self.exit()
            # Let the modal handle all other keys
            return
        
        # Block left/right arrow keys for table navigation
        if event.key in ["left", "right"]:
            event.prevent_default()
            return
        
        if event.key == "space":
            self.player.toggle_playback()
        elif event.key == "ctrl+c":
            self.exit()
        elif event.key == "ctrl+shift+k":
            # Open command prompt
            self._open_command_prompt()
        elif event.key == "ctrl+shift+s":
            # Shuffle Playlist
            self._shuffle_playlist()
        elif event.key == "ctrl+shift+t":
            # Open settings (moved from ctrl+shift+s)
            self._open_settings()
        elif event.key == "ctrl+shift+d":
            # Open download screen
            self._open_download_screen()
        elif event.key == "ctrl+shift+q":
            # Open queue screen
            self._open_queue_screen()
        elif event.key == "ctrl+shift+up":
            # Page up
            self._page_up()
        elif event.key == "ctrl+shift+down":
            # Page down
            self._page_down()
        elif event.key == "ctrl+shift+right":
            # Skip song (triggers song ending callback)
            self._skip_song()
        elif event.key == "ctrl+shift+left":
            # Previous song or reset current song
            self._previous_or_reset_song()
        elif event.key == "ctrl+shift+u":
            # Start download for current playlist
            self._start_current_playlist_download()
        elif event.key == "ctrl+shift+a":
            # Shuffle all songs from all playlists
            self._shuffle_all_songs()
        elif event.key == "ctrl+shift+f":
            # Download all playlists
            self._download_all_playlists()
        elif event.key == "cmd+ctrl+up":
            # Move to top of playlist
            self._move_to_top()
        elif event.key == "cmd+ctrl+down":
            # Move to bottom of playlist
            self._move_to_bottom()
        elif event.key == "enter":
            # Enter key to play selected song and generate new queue
            songs_table = self.query_one("#content-table", DataTable)
            if songs_table.cursor_row < len(self.sorted_indices):
                # Get the original index from the sorted display
                original_index = self.sorted_indices[songs_table.cursor_row]
                selected_song = self.songs[original_index]
                self._play_song_and_generate_queue(selected_song)
        elif event.key == "shift+enter":
            # Shift+Enter to add selected song to top of queue
            songs_table = self.query_one("#content-table", DataTable)
            if songs_table.cursor_row < len(self.sorted_indices):
                # Get the original index from the sorted display
                original_index = self.sorted_indices[songs_table.cursor_row]
                selected_song = self.songs[original_index]
                self._add_song_to_queue(selected_song)
    
    @on(DataTable.HeaderSelected)
    def on_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        """Handle column header clicks for sorting."""
        column_key = event.column_key
        if column_key in ["song", "artist", "duration", "date"]:
            # Remember which song was highlighted before sorting
            songs_table = self.query_one("#content-table", DataTable)
            highlighted_song_path = None
            if songs_table.cursor_row < len(self.sorted_indices):
                highlighted_original_index = self.sorted_indices[songs_table.cursor_row]
                highlighted_song_path = self.songs[highlighted_original_index]
            
            self._sort_songs(column_key)
            self._update_list_view()
            
            # Try to preserve cursor position on the previously highlighted song
            if highlighted_song_path:
                try:
                    # Find the new display position of the previously highlighted song
                    original_index = self.songs.index(highlighted_song_path)
                    new_display_index = self.sorted_indices.index(original_index)
                    songs_table.move_cursor(row=new_display_index)
                except (ValueError, IndexError):
                    # If we can't find the song, move cursor to currently playing song if any
                    self._move_cursor_to_current_song()

    @on(DataTable.RowSelected)
    def on_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle table row selection - check for double click."""
        current_time = time.time()
        current_index = event.cursor_row
        
        # Check if this is a double-click (within 0.5 seconds and same item)
        is_double_click = (
            current_time - self.last_click_time < 0.5 and  # 0.5 seconds
            current_index == self.last_click_index
        )
        
        self.last_click_time = current_time
        self.last_click_index = current_index
        
        # For songs, only double-click plays and generates new queue
        if is_double_click and current_index < len(self.songs):
            # Get the original index from the sorted display
            if current_index < len(self.sorted_indices):
                original_index = self.sorted_indices[current_index]
                selected_song = self.songs[original_index]
                self._play_song_and_generate_queue(selected_song)
    
    def _open_command_prompt(self) -> None:
        """Open the command prompt modal."""
        def handle_result(result):
            # Clear modal flag when command prompt closes
            self.modal_active = False
            
            if result is not None:
                result_type, path = result
                if result_type == "shuffle":
                    # Shuffle playlist
                    self._shuffle_playlist()
                elif result_type == "shuffle_all":
                    # Shuffle all songs from all playlists
                    self._shuffle_all_songs()
                elif result_type == "settings":
                    # Open settings screen
                    self._open_settings()
                elif result_type == "queue":
                    # Open queue screen
                    self._open_queue_screen()
                elif result_type == "download":
                    # Open download screen
                    self._open_download_screen()
                elif result_type == "download_playlist":
                    # Start download for current playlist
                    self._start_current_playlist_download()
                elif result_type == "download_all":
                    # Start download for all playlists
                    self._download_all_playlists()
                elif result_type == "playlist":
                    # Store current playback state to preserve state
                    was_playing = self.player.is_playing
                    current_song_path = self.player.song_path
                    
                    # Save current playlist download state before switching
                    self._save_current_playlist_state()
                    
                    # Switch to the selected playlist
                    self.current_playlist = path
                    self._set_current_playlist_state(path)  # Load playlist-specific download state
                    self._load_songs(path)
                    self._update_list_view()
                    
                    # Move cursor to currently playing song if it exists in this playlist, otherwise first row
                    self._move_cursor_to_current_song()
                    if self._get_current_song_display_index() == -1:
                        # Current song not in this playlist, move to first row
                        songs_table = self.query_one("#content-table", DataTable)
                        if len(self.songs) > 0:
                            songs_table.move_cursor(row=0)
                    
                    # If a song was playing before, make sure it continues playing
                    # (don't restart it, just ensure it keeps playing)
                    if was_playing and current_song_path and self.player.song_path == current_song_path:
                        # Song is still the same, make sure it's still playing
                        if not self.player.is_playing:
                            self.player.toggle_playback()
                elif result_type == "song":
                    # Find the playlist containing this song and switch to it
                    for playlist_name, songs in self.all_songs.items():
                        if path in songs:
                            # Save current playlist download state before switching
                            self._save_current_playlist_state()
                            
                            self.current_playlist = playlist_name
                            self._set_current_playlist_state(playlist_name)  # Load playlist-specific download state
                            self._load_songs(playlist_name)
                            self._update_list_view()
                            # Find the song's index and highlight it
                            try:
                                song_index = self.songs.index(path)
                                # Move cursor to the song's display position
                                display_index = self.sorted_indices.index(song_index)
                                songs_table = self.query_one("#content-table", DataTable)
                                songs_table.move_cursor(row=display_index)
                                # Play the song and generate new queue from this playlist view
                                self._play_song_and_generate_queue(path)
                            except ValueError:
                                pass  # Song not found in current playlist
                            break
        
        # Set modal flag when command prompt opens
        self.modal_active = True
        
        # Create and show the command prompt
        command_prompt = CommandPrompt(self.playlists, self.all_songs, self)
        self.push_screen(command_prompt, handle_result)
    
    def _open_settings(self) -> None:
        """Open the settings screen."""
        def handle_settings_result(settings_changed):
            # Clear modal flag when settings screen closes
            self.modal_active = False
            
            if settings_changed:
                # Save current state before reloading
                self._save_current_playlist_state()
                
                # Reload playlists if settings changed
                old_playlist = self.current_playlist
                self._load_playlists()
                
                # Try to restore current playlist if it still exists
                if old_playlist and old_playlist in self.playlists:
                    self.current_playlist = old_playlist
                    self._set_current_playlist_state(old_playlist)  # Restore playlist-specific state
                    self._load_songs(old_playlist)
                elif self.playlists:
                    # Fall back to first playlist
                    self.current_playlist = self.playlists[0]
                    self._set_current_playlist_state(self.current_playlist)  # Load state for first playlist
                    self._load_songs(self.current_playlist)
                else:
                    # No playlists available
                    self.current_playlist = None
                    self._download_logs = []
                    self._download_status = ""
                    self.songs = []
                    self.sorted_indices = []
                
                # Update the display
                self._update_list_view()
        
        # Set modal flag when settings screen opens
        self.modal_active = True
        
        # Create and show the settings screen
        settings_screen = SettingsScreen(self.settings)
        self.push_screen(settings_screen, handle_settings_result)
    
    def _get_playlist_download_state(self, playlist_name: str) -> Dict:
        """Get download state for a specific playlist."""
        if playlist_name not in self._playlist_download_state:
            self._playlist_download_state[playlist_name] = {
                'logs': [],
                'status': '',
                'downloading': False,
                'thread': None
            }
        return self._playlist_download_state[playlist_name]
    
    def _set_current_playlist_state(self, playlist_name: str):
        """Set current download state to match the given playlist."""
        if not playlist_name:
            self._download_logs = []
            self._download_status = ""
            return
            
        state = self._get_playlist_download_state(playlist_name)
        self._download_logs = state['logs']
        self._download_status = state['status']
        # Note: _downloading tracks active download, not per-playlist
    
    def _save_current_playlist_state(self):
        """Save current download state to the current playlist."""
        if self.current_playlist:
            state = self._get_playlist_download_state(self.current_playlist)
            state['logs'] = self._download_logs.copy()
            state['status'] = self._download_status
            # Note: downloading and thread are managed separately per playlist
    
    def _add_download_log(self, line: str, playlist_name: str = None):
        """Add a line to the download log buffer for a specific playlist."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {line}"
        
        # Determine which playlist to log to
        target_playlist = playlist_name or self.current_playlist
        if not target_playlist:
            return
        
        # Add to playlist-specific state
        state = self._get_playlist_download_state(target_playlist)
        state['logs'].append(log_line)
        
        # Keep only last 100 lines
        if len(state['logs']) > 100:
            state['logs'] = state['logs'][-100:]
        
        # If this is the current playlist, also update current state
        if target_playlist == self.current_playlist:
            self._download_logs = state['logs'].copy()
    
    def _start_current_playlist_download(self) -> None:
        """Start download for the currently selected playlist directly from main view."""
        if not self.current_playlist:
            return
        
        # Check if this specific playlist is already downloading
        state = self._get_playlist_download_state(self.current_playlist)
        if state['downloading']:
            return
        
        playlist_name = self.current_playlist  # Capture playlist name for the thread
        
        def download_async():
            try:
                # Set downloading state for this playlist
                download_state = self._get_playlist_download_state(playlist_name)
                download_state['downloading'] = True
                download_state['status'] = "Updating..."
                
                # Clear previous logs and start fresh for this playlist
                download_state['logs'] = []
                self._add_download_log(f"Starting download for playlist: {playlist_name}", playlist_name)
                
                def progress_callback(current: int, total: int, message: str):
                    # Add progress messages to logs for this specific playlist
                    if total > 0:
                        self._add_download_log(f"[{current}/{total}] {message}", playlist_name)
                    else:
                        self._add_download_log(message, playlist_name)
                
                # Call our download function with progress callback
                success = download_playlist(
                    playlist_name,
                    progress_callback=progress_callback
                )
                
                if success:
                    self._add_download_log("Download completed successfully!", playlist_name)
                    # Set "Updated last at" status
                    download_state['status'] = f"Updated last at {datetime.now().strftime('%H:%M %m/%d')}"
                    
                    # Refresh songs and search indexes only if this is still the current playlist
                    if playlist_name == self.current_playlist:
                        self._load_songs(self.current_playlist)
                        self._update_list_view()
                        self._download_status = download_state['status']
                    
                    # Always refresh search indexes for all playlists
                    self._load_playlists()
                else:
                    self._add_download_log("Download failed!", playlist_name)
                    download_state['status'] = "Update failed"
                    
                    # Update current status if this is the current playlist
                    if playlist_name == self.current_playlist:
                        self._download_status = download_state['status']
                
            except Exception as e:
                self._add_download_log(f"Error: {str(e)}", playlist_name)
                download_state['status'] = f"Update failed: {str(e)}"
                
                # Update current status if this is the current playlist
                if playlist_name == self.current_playlist:
                    self._download_status = download_state['status']
            finally:
                download_state['downloading'] = False
                download_state['thread'] = None
        
        # Start download in separate thread
        download_thread = threading.Thread(target=download_async)
        download_thread.daemon = True
        state['thread'] = download_thread
        download_thread.start()
    
    def _download_all_playlists(self) -> None:
        """Start download for all configured playlists."""
        if not self.playlists:
            self.notify("No playlists configured")
            return
        
        # Count how many playlists are already downloading
        already_downloading = 0
        for playlist_name in self.playlists:
            state = self._get_playlist_download_state(playlist_name)
            if state['downloading']:
                already_downloading += 1
        
        if already_downloading == len(self.playlists):
            self.notify("All playlists are already downloading")
            return
        
        # Start downloads for all playlists that aren't already downloading
        started_downloads = 0
        for playlist_name in self.playlists:
            state = self._get_playlist_download_state(playlist_name)
            if not state['downloading']:
                self._start_playlist_download_async(playlist_name)
                started_downloads += 1
        
        # Show notification
        if started_downloads > 0:
            total_msg = f"[+] Started downloads for {started_downloads} playlist"
            if started_downloads > 1:
                total_msg += "s"
            if already_downloading > 0:
                total_msg += f" ({already_downloading} already downloading)"
            # Toast notification removed
        # else block removed since no notification needed
    
    def _start_playlist_download_async(self, playlist_name: str) -> None:
        """Start download for a specific playlist asynchronously."""
        # Check if this specific playlist is already downloading
        state = self._get_playlist_download_state(playlist_name)
        if state['downloading']:
            return
        
        def download_async():
            try:
                # Set downloading state for this playlist
                download_state = self._get_playlist_download_state(playlist_name)
                download_state['downloading'] = True
                download_state['status'] = "Updating..."
                
                # Clear previous logs and start fresh for this playlist
                download_state['logs'] = []
                self._add_download_log(f"Starting download for playlist: {playlist_name}", playlist_name)
                
                def progress_callback(current: int, total: int, message: str):
                    # Add progress messages to logs for this specific playlist
                    if total > 0:
                        self._add_download_log(f"[{current}/{total}] {message}", playlist_name)
                    else:
                        self._add_download_log(message, playlist_name)
                
                # Call our download function with progress callback
                success = download_playlist(
                    playlist_name,
                    progress_callback=progress_callback
                )
                
                if success:
                    self._add_download_log("Download completed successfully!", playlist_name)
                    # Set "Updated last at" status
                    download_state['status'] = f"Updated last at {datetime.now().strftime('%H:%M %m/%d')}"
                    
                    # Refresh songs and search indexes only if this is still the current playlist
                    if playlist_name == self.current_playlist:
                        self._load_songs(self.current_playlist)
                        self._update_list_view()
                        self._download_status = download_state['status']
                    
                    # Always refresh search indexes for all playlists
                    self._load_playlists()
                else:
                    self._add_download_log("Download failed!", playlist_name)
                    download_state['status'] = "Update failed"
                    
                    # Update current status if this is the current playlist
                    if playlist_name == self.current_playlist:
                        self._download_status = download_state['status']
                
            except Exception as e:
                self._add_download_log(f"Error: {str(e)}", playlist_name)
                download_state['status'] = f"Update failed: {str(e)}"
                
                # Update current status if this is the current playlist
                if playlist_name == self.current_playlist:
                    self._download_status = download_state['status']
            finally:
                download_state['downloading'] = False
                download_state['thread'] = None
        
        # Start download in separate thread
        download_thread = threading.Thread(target=download_async)
        download_thread.daemon = True
        state['thread'] = download_thread
        download_thread.start()
    
    def _open_queue_screen(self) -> None:
        """Open the queue view screen."""
        def handle_queue_result(queue_changed):
            # Clear modal flag when queue screen closes
            self.modal_active = False
        
        # Set modal flag when queue screen opens
        self.modal_active = True
        
        # Create and show the queue screen
        queue_screen = QueueScreen(self)
        self.push_screen(queue_screen, handle_queue_result)
    
    def _open_download_screen(self) -> None:
        """Open the download output screen to show logs from current/last download."""
        if not self.current_playlist:
            return
        
        def handle_download_result(download_completed):
            # Clear modal flag when download screen closes
            self.modal_active = False
        
        # Set modal flag when download screen opens
        self.modal_active = True
        
        # Get playlist-specific download state
        state = self._get_playlist_download_state(self.current_playlist)
        
        # Create and show the download logs screen (no new download)
        download_screen = DownloadLogsScreen(
            self.current_playlist, 
            state['logs'].copy(),  # Pass playlist-specific logs
            state['downloading'],  # Pass playlist-specific download status
            self  # Pass app instance for live updates
        )
        self.push_screen(download_screen, handle_download_result)
    
    def _global_toggle_playback(self) -> None:
        """Global handler for play/pause toggle from media keys."""
        print("Global toggle playback called")
        self.player.toggle_playback()
    
    def _global_skip_song(self) -> None:
        """Global handler for skip song from media keys."""
        print("Global skip song called")
        self._skip_song()
    
    def _global_previous_song(self) -> None:
        """Global handler for previous song from media keys."""
        print("Global previous song called")
        self._previous_or_reset_song()
    
    def on_unmount(self) -> None:
        """Cleanup when app exits."""
        # Stop global hotkey manager
        if hasattr(self, 'global_hotkey_manager'):
            self.global_hotkey_manager.stop()
        
        if self.update_timer:
            self.update_timer.stop()
        self.player.stop()
        pygame.mixer.quit()


def main():
    """Main entry point."""
    app = MusicPlayerApp()
    app.run()


if __name__ == "__main__":
    main()