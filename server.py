import os

import requests
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Union, Optional
from typing import Annotated

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

mcp = FastMCP('search-api')

# Base API URL
url = os.getenv("NB_SEARCH_URL")

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
def search_api(q: Annotated[str, Field(description='Search query string. This is the main search parameter.')],
               size: Annotated[Union[int, float], Field(description='Number of results to return. Default is 10, maximum recommended is 100.')] = 10,
               location: Annotated[Optional[str], Field(description='Location filter for search results. Can be a city, state, country, or geographic area.')] = None,
               latitude: Annotated[Optional[Union[int, float]], Field(description='Latitude coordinate for geographic search filtering.')] = None,
               longitude: Annotated[Optional[Union[int, float]], Field(description='Longitude coordinate for geographic search filtering.')] = None) -> dict:
    '''Search API that provides comprehensive search results with optional geographic filtering. Supports text queries with location-based refinement using either location names or coordinates.'''

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
        response = requests.get(url, params=params, timeout=30)
        
        # Check if request was successful
        if response.status_code != 200:
            return {
                'error': f'API request failed with status code: {response.status_code}',
                'status_code': response.status_code
            }
        
        # Return the JSON response
        return response.json()
        
    except requests.exceptions.Timeout:
        return {'error': 'Request timeout - API took too long to respond'}
    except requests.exceptions.ConnectionError:
        return {'error': 'Connection error - Unable to connect to the API'}
    except requests.exceptions.RequestException as e:
        return {'error': f'Request error: {str(e)}'}
    except ValueError as e:
        return {'error': f'JSON parsing error: {str(e)}'}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


def run_test():
    params = {'q': "trump", 'size': 2}
    requests.get(url, params=params, timeout=10)


if __name__ == "__main__":
    # run_test()
    mcp.run(transport="stdio")
