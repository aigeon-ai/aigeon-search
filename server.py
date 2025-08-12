import logging
import os

import aiohttp
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from typing import Union, Optional
from typing import Annotated

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
rapid_api_key = os.getenv("RAPID_API_KEY")

__rapidapi_url__ = 'https://rapidapi.com/particle-media-particle-media-default/api/aigeon-news-search1'

mcp = FastMCP('search-api')

def parse_val(value, target_type):
    """Parse and convert value to target type with error handling"""
    if value is None:
        return None
    try:
        if target_type == str:
            return str(value)
        elif target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        else:
            return value
    except (ValueError, TypeError):
        return None

@mcp.tool()
async def news_search(q: Annotated[str, Field(description='Search query string. This is the main search parameter.')],
               size: Annotated[Union[int, float], Field(description='Number of results to return. Default is 10, maximum recommended is 100.')] = 10,
               location: Annotated[Optional[str], Field(description='Location filter for search results. Can be a city, state, country, or geographic area.')] = None,
               latitude: Annotated[Optional[Union[int, float]], Field(description='Latitude coordinate for geographic search filtering.')] = None,
               longitude: Annotated[Optional[Union[int, float]], Field(description='Longitude coordinate for geographic search filtering.')] = None) -> dict:
    '''News Search API that provides comprehensive news search results with optional geographic filtering. Supports text queries with location-based refinement using either location names or coordinates.'''

    url = "https://aigeon-news-search1.p.rapidapi.com/api/search"
    headers = {'x-rapidapi-host': 'aigeon-news-search1.p.rapidapi.com', 'x-rapidapi-key': rapid_api_key}

    # Parse and validate parameters
    query = parse_val(q, str)
    size_val = parse_val(size, int)
    location_val = parse_val(location, str)
    latitude_val = parse_val(latitude, float)
    longitude_val = parse_val(longitude, float)
    
    # Process location parameter (replace underscores and commas with spaces)
    if location_val:
        location_val = location_val.replace("_", " ").replace(",", " ")
    
    # Build request parameters
    params = {
        'q': query,
        'size': size_val,
    }
    
    # Add optional parameters if provided
    if location_val:
        params['location'] = location_val
    if latitude_val is not None:
        params['latitude'] = latitude_val
    if longitude_val is not None:
        params['longitude'] = longitude_val
    
    try:
        # Make the API request
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=5, raise_for_status=True, headers=headers) as r:
                response = await r.json()
                if isinstance(response, list):
                    return {"result": response}
                return response
    except Exception as e:
        logging.warning("", exc_info=True)
        return {"status": "failed", "reason": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
