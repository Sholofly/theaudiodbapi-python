"""Test for TheAudioDB Api integration."""
import asyncio
import logging
from theaudiodbapi import TheAudioDBApi
from api_key import API_KEY
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger()

async def test():
    """Function to test TheAudioDBAPI integration"""
    api = TheAudioDBApi(api_key=API_KEY)
    await _update(api)
    await api.close()


async def _update(api:TheAudioDBApi):
    """Update and print"""
    track_info = await api.get_track_info("Coldplay", "Fix you")



loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()
