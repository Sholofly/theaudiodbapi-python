"""Class for managing one TheAudioDB API integration."""
from __future__ import annotations

import asyncio
import json
import logging
import socket
import async_timeout
import backoff

from yarl import URL
from aiohttp import ClientResponse, ClientSession, ClientError

from typing import Any, Dict, List
from .const import API_HOST
from .exceptions import (
    TheAudioDBApiConnectionError,
    TheAudioDBApiConnectionTimeoutError,
    TheAudioDBApiError,
    TheAudioDBApiRateLimitError,
)

from .models import (
    TheAudioDBTrackInfo
)

_LOGGER = logging.getLogger(__name__)

class TheAudioDBApi:
    """ Main class to control the TheAudioDB API"""
    _api_key: str = None
    def __init__(
        self,
        *,
        api_key: str,       
    ) -> None:
        """Initialize connection with the TheAudioDB API."""
        self._api_key = api_key

    @backoff.on_exception(backoff.expo, TheAudioDBApiConnectionError, max_tries=3, logger=_LOGGER)
    @backoff.on_exception(
        backoff.expo, TheAudioDBApiRateLimitError, base=60, max_tries=6, logger=_LOGGER
    )
    async def _request(self, method, uri, **kwargs) -> ClientResponse:
        """Make a request."""
        if self.token_refresh_method is not None:
            self.token = await self.token_refresh_method()
            _LOGGER.debug(f'Token refresh method called.')
        
        url = URL.build(
            scheme='https',
            host=API_HOST,
        ) 
        url = str(url) + uri
        _LOGGER.debug(f'Executing {method} API request to {url}.')
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)


        headers["X-RapidAPI-Key"] = self._api_key
        headers["X-RapidAPI-Host"] = API_HOST

        _LOGGER.debug(f'With headers:')
        _LOGGER.debug(f'{str(headers)}')
        if self._session is None:
            self._session = ClientSession()
            _LOGGER.debug(f'New session created.')
            self._close_session = True

        try:
            with async_timeout.timeout(self.request_timeout):
                response =  await self._session.request(
                    method,
                    f"{url}",
                    **kwargs,
                    headers=headers,
                )
        except asyncio.TimeoutError as exception:
            raise TheAudioDBApiConnectionTimeoutError(
                "Timeout occurred while connecting to the TheAudioDB API"
            ) from exception
        except (ClientError, socket.gaierror) as exception:
            raise TheAudioDBApiConnectionError(
                "Error occurred while communicating with the TheAudioDB API"
            ) from exception
        
        content_type = response.headers.get("Content-Type", "")
        # Error handling
        if (response.status // 100) in [4, 5]:
            contents = await response.read()
            response.close()

            if response.status == 429:
                raise TheAudioDBApiRateLimitError(
                    "Rate limit error has occurred with the TheAudioDB API"
                )

            if content_type == "application/json":
                raise TheAudioDBApiError(response.status, json.loads(contents.decode("utf8")))
            raise TheAudioDBApiError(response.status, {"message": contents.decode("utf8")})
        
        # Handle empty response
        if response.status == 204:
            _LOGGER.warning(f'Request to {url} resulted in status 204. Your dataset could be out of date.')
            return
        
        if "application/json" in content_type:
            result =  await response.json()
            _LOGGER.debug(f'Response:')
            _LOGGER.debug(f'{str(result)}')
            return result
        result =  await response.text()
        _LOGGER.debug(f'Response:')
        _LOGGER.debug(f'{str(result)}')
        return result

    async def get_track_info(self, artist:str, track:str) -> TheAudioDBTrackInfo:
        """Returns first track info for a search string"""
        data = await self._request("GET", f"/searchtrack.php",params={"s":artist, "t":track})
        if not 'track' in data or len(data['track']) == 0:
            return None
        return TheAudioDBTrackInfo(data['track'][0])
        
    async def __aenter__(self) -> TheAudioDBApi:
        """Async enter."""
        return self
    
    async def __aexit__(self, *exc_info) -> None:
        """Async exit."""
        await self.close()
        