# -*- coding: utf-8 -*-
import json
from datetime import datetime, date
from tornado.escape import json_decode
from typing import Dict, Any, Union, Optional

from yitool.log import logger
from yitool.utils.path_utils import PathUtils
from yitool.exceptions import YiToolException

# Custom JSON encoder for handling datetime and date types
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        # Handle datetime objects
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
            # return obj.isoformat()
        # Handle date objects
        elif isinstance(obj, date):
            # return obj.isoformat()
            return obj.strftime('%Y-%m-%d')
        return super().default(obj)

class JsonUtils:
    """JSON utility class that provides functions for handling JSON files and data"""
    
    @staticmethod
    def load(json_file: str) -> Any:
        """Load JSON data from a file
        
        Args:
            json_file: Path to the JSON file
        
        Returns:
            The loaded JSON data (typically a dictionary or list)
        
        Raises:
            FileNotFoundError: If the file does not exist
            YiToolException: If JSON parsing fails
        """
        PathUtils.raise_if_not_exists(json_file)
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as exc:
            logger.error(f'Failed to parse JSON file: {json_file}. Error: {str(exc)}')
            raise YiToolException(f'Failed to parse JSON file: {json_file}. Error: {str(exc)}') from exc
        except Exception as exc:
            logger.error(f'Error loading JSON file: {json_file}. Error: {str(exc)}')
            raise YiToolException(f'Error loading JSON file: {json_file}. Error: {str(exc)}') from exc
        
    @staticmethod
    def dump(json_file: str, data: Union[Dict[str, Any], list, Any]):
        """Save data to a JSON file
        
        Args:
            json_file: Path to the output JSON file
            data: The data to save (must be JSON serializable)
        
        Raises:
            YiToolException: If saving data fails
        """
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
        except (TypeError, OverflowError) as exc:
            logger.error(f'Failed to serialize data to JSON. Error: {str(exc)}')
            raise YiToolException(f'Failed to serialize data to JSON. Error: {str(exc)}') from exc
        except Exception as exc:
            logger.error(f'Error writing to JSON file: {json_file}. Error: {str(exc)}')
            raise YiToolException(f'Error writing to JSON file: {json_file}. Error: {str(exc)}') from exc
            
    @staticmethod
    def json_decode(json_str: str) -> dict[str, Any]:
        """Decode a JSON string into a Python dictionary
        
        Args:
            json_str: A JSON formatted string
        
        Returns:
            The decoded Python dictionary
        
        Raises:
            YiToolException: If decoding fails
        """
        try:
            return json_decode(json_str)
        except Exception as exc:
            logger.error(f'Failed to decode JSON string. Error: {str(exc)}')
            raise YiToolException(f'Failed to decode JSON string. Error: {str(exc)}') from exc

    @staticmethod
    def json_encode(value: Any) -> str:
        """Encode a Python object into a JSON string
        
        Args:
            value: The Python object to encode (must be JSON serializable)
        
        Returns:
            The encoded JSON string
        
        Raises:
            YiToolException: If encoding fails
        """
        try:
            return json.dumps(value, ensure_ascii=False, cls=DateTimeEncoder)
        except (TypeError, OverflowError) as exc:
            logger.error(f'Failed to encode data to JSON string. Error: {str(exc)}')
            raise YiToolException(f'Failed to encode data to JSON string. Error: {str(exc)}') from exc