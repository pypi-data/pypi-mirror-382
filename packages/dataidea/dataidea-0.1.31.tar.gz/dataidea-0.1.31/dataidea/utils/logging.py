"""
Logging utilities for tracking events and LLM usage
"""
import requests
import logging
from dataidea.utils.printing import print

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def event_log(data):
    """
    Log an event to the DATAIDEA LOGGER API.
    
    Parameters:
    -----------
    data : dict
        Dictionary containing the event data with the following keys:
        - api_key: API key for authentication
        - project_name: Name of the project
        - user_id: User identifier
        - message: Event message
        - level: Log level (e.g., 'info', 'error')
        - metadata: Additional metadata (optional)
        
    Returns:
    --------
    int
        HTTP status code from the API response
        
    Example:
    --------
    >>> event_log({
    ...     'api_key': '1234567890',
    ...     'project_name': 'Test Project',
    ...     'user_id': '1234567890',
    ...     'message': 'This is a test message',
    ...     'level': 'info',
    ...     'metadata': {'test': 'test'}
    ... })
    Event logged successfully
    201
    """
    required_fields = ['api_key', 'project_name', 'user_id', 'message', 'level']
    for field in required_fields:
        if field not in data:
            logger.error(f"Missing required field: {field}")
            return 400
    
    url = 'https://logger.api.dataidea.org/api/event-log/'
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 201:
            print('[green]Event logged successfully[/green]')
        else:
            print(f'[red]Failed to log event: {response.status_code}[/red]')
        
        return response.status_code
    except Exception as e:
        logger.error(f"Error sending event log: {e}")
        return 500

def llm_log(data):
    """
    Log an LLM event to the DATAIDEA LOGGER API.
    
    Parameters:
    -----------
    data : dict
        Dictionary containing the LLM event data with the following keys:
        - api_key: API key for authentication
        - project_name: Name of the project
        - user_id: User identifier
        - source: Source of the LLM (e.g., 'llm')
        - query: User query
        - response: LLM response
        
    Returns:
    --------
    int
        HTTP status code from the API response
        
    Example:
    --------
    >>> llm_log({
    ...     'api_key': '1234567890',
    ...     'project_name': 'Test Project',
    ...     'user_id': '1234567890',
    ...     'source': 'llm',
    ...     'query': 'This is a test query',
    ...     'response': 'This is a test response',
    ... })
    LLM event logged successfully
    201
    """
    required_fields = ['api_key', 'project_name', 'user_id', 'source', 'query', 'response']
    for field in required_fields:
        if field not in data:
            logger.error(f"Missing required field: {field}")
            return 400
    
    url = 'https://logger.api.dataidea.org/api/llm-log/'
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 201:
            print('[green]LLM event logged successfully[/green]')
        else:
            print(f'[red]Failed to log LLM event: {response.status_code}[/red]')
        
        return response.status_code
    except Exception as e:
        logger.error(f"Error sending LLM log: {e}")
        return 500

__all__ = ['event_log', 'llm_log'] 