from __future__ import annotations
from array import array
from enum import Enum
from typing import Any, Dict, Optional, TypedDict

from dataclasses import dataclass
from datetime import datetime
from .utils import try_get_from_dict

@dataclass
class TheAudioDBTrackInfo:
    "Class to hold TheAudioDB track information"
    artist_name:str = None
    alternate_artist_name: str = None
    album_name:str = None
    name:str = None
    description:str = None
    track_thumb:str = None
    
    def __init__(self, *, data: Dict[str, Any]) -> TheAudioDBTrackInfo:
        self.name = try_get_from_dict(data, 'strTrack', self.name)
        self.artist_name = try_get_from_dict(data, 'strArtist', self.artist_name)
        self.album_name = try_get_from_dict(data, 'strAlbum', self.album_name)
        self.alternate_artist_name = try_get_from_dict(data, 'strArtistAlternate', self.alternate_artist_name)
        self.description = try_get_from_dict(data, 'strDescriptionEN', self.description)
        self.track_thumb = try_get_from_dict(data, 'strTrackThumb', self.track_thumb)
