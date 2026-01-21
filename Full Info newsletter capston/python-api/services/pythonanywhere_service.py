#!/usr/bin/env python3
"""
PythonAnywhere Service
Handles API calls to PythonAnywhere for system monitoring and data collection.
"""

import requests
import os
import logging
import csv
import io
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PythonAnywhereService:
    def __init__(self):
        self.username = os.getenv('PYTHONANYWHERE_USERNAME', 'CJSlattery')
        self.token = os.getenv('PYTHONANYWHERE_TOKEN', 'PUBLIC-FILLER-REPLACE-API-KEY-HERE')
        self.base_url = 'https://www.pythonanywhere.com/api/v0'
        self.headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }
    
    async def get_cpu_quota(self) -> Dict[str, Any]:
        """
        Get CPU quota information from PythonAnywhere
        
        Returns:
            Dict: CPU quota information
        """
        try:
            url = f'{self.base_url}/user/{self.username}/cpu/'
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Successfully retrieved CPU quota info")
                return {
                    'success': True,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.warning(f"Unexpected status code {response.status_code}: {response.content}")
                return {
                    'success': False,
                    'error': f'Status code {response.status_code}',
                    'message': response.content.decode('utf-8'),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting CPU quota: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_consoles(self) -> Dict[str, Any]:
        """
        Get console information from PythonAnywhere
        
        Returns:
            Dict: Console information
        """
        try:
            url = f'{self.base_url}/user/{self.username}/consoles/'
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Successfully retrieved console info")
                return {
                    'success': True,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.warning(f"Unexpected status code {response.status_code}: {response.content}")
                return {
                    'success': False,
                    'error': f'Status code {response.status_code}',
                    'message': response.content.decode('utf-8'),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting console info: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_files(self, path: str = '/home/CJSlattery/') -> Dict[str, Any]:
        """
        Get file listing from PythonAnywhere
        
        Args:
            path (str): Path to list files from
            
        Returns:
            Dict: File listing information
        """
        try:
            url = f'{self.base_url}/user/{self.username}/files/path{path}'
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully retrieved file listing for {path}")
                return {
                    'success': True,
                    'data': data,
                    'path': path,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.warning(f"Unexpected status code {response.status_code}: {response.content}")
                return {
                    'success': False,
                    'error': f'Status code {response.status_code}',
                    'message': response.content.decode('utf-8'),
                    'path': path,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting file listing: {e}")
            return {
                'success': False,
                'error': str(e),
                'path': path,
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status from PythonAnywhere
        
        Returns:
            Dict: Complete system status information
        """
        try:
            # Get multiple pieces of information
            cpu_quota = await self.get_cpu_quota()
            consoles = await self.get_consoles()
            files = await self.get_files()
            
            return {
                'success': True,
                'system_status': {
                    'cpu_quota': cpu_quota,
                    'consoles': consoles,
                    'files': files
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def read_csv_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read a CSV file from PythonAnywhere and parse it
        
        Args:
            file_path (str): Path to CSV file (e.g., '/home/CJSlattery/CSVs/recentIPOS.csv')
            
        Returns:
            Dict: Parsed CSV data
        """
        try:
            # First get the file content URL
            url = f'{self.base_url}/user/{self.username}/files/path{file_path}'
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                # Check if response has content
                if not response.content:
                    logger.warning(f"Empty response for file path: {file_path}")
                    return {
                        'success': False,
                        'error': 'Empty response from PythonAnywhere API',
                        'file_path': file_path,
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Initialize csv_content variable
                csv_content = None
                
                # Try to parse as JSON first (in case it's a file info object)
                logger.info(f"Attempting to parse response as JSON for {file_path}")
                try:
                    file_info = response.json()
                    logger.info(f"Successfully parsed as JSON, got file_info: {file_info}")
                    # If it's JSON, check if it has a URL to download
                    file_url = file_info.get('url')
                    if file_url:
                        # Download the file content from the URL
                        file_response = requests.get(file_url, headers=self.headers, timeout=30)
                        if file_response.status_code == 200:
                            csv_content = file_response.content.decode('utf-8').strip()
                        else:
                            logger.warning(f"Could not download file content: {file_response.status_code}")
                            return {
                                'success': False,
                                'error': f'Could not download file: {file_response.status_code}',
                                'file_path': file_path,
                                'timestamp': datetime.now().isoformat()
                            }
                    else:
                        # JSON response but no URL - might be file listing or other structure
                        logger.warning(f"No URL found in JSON response for file: {file_path}")
                        return {
                            'success': False,
                            'error': 'No URL found for file',
                            'file_path': file_path,
                            'timestamp': datetime.now().isoformat()
                        }
                except (ValueError, json.JSONDecodeError) as json_error:
                    # Response is not JSON - it's likely the CSV content directly
                    logger.info(f"Response is not JSON, treating as CSV directly: {type(json_error).__name__}")
                    csv_content = response.content.decode('utf-8').strip()
                
                # Ensure csv_content is set
                if csv_content is None:
                    csv_content = response.content.decode('utf-8').strip()
                
                # Check if CSV content is empty
                if not csv_content:
                    logger.warning(f"CSV file {file_path} is empty")
                    return {
                        'success': False,
                        'error': 'CSV file is empty',
                        'data': [],
                        'row_count': 0,
                        'file_path': file_path,
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Parse CSV content
                try:
                    csv_reader = csv.DictReader(io.StringIO(csv_content))
                    data = list(csv_reader)
                    
                    logger.info(f"Successfully read CSV file {file_path} with {len(data)} rows")
                    return {
                        'success': True,
                        'data': data,
                        'row_count': len(data),
                        'file_path': file_path,
                        'timestamp': datetime.now().isoformat()
                    }
                except Exception as parse_error:
                    logger.error(f"Error parsing CSV content from {file_path}: {parse_error}")
                    logger.error(f"CSV content preview: {csv_content[:200]}")
                    return {
                        'success': False,
                        'error': f'Error parsing CSV: {str(parse_error)}',
                        'data': [],
                        'row_count': 0,
                        'file_path': file_path,
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                logger.warning(f"File not found: {file_path} (status {response.status_code})")
                return {
                    'success': False,
                    'error': f'File not found: {response.status_code}',
                    'file_path': file_path,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path,
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_recent_ipos(self) -> Dict[str, Any]:
        """
        Get recent IPOs from the recentIPOS.csv file
        
        Returns:
            Dict: Recent IPO data from CSV
        """
        return await self.read_csv_file('/home/CJSlattery/CSVs/recentIPOS.csv')
    
    async def get_upcoming_ipos(self) -> Dict[str, Any]:
        """
        Get upcoming IPOs from the upcomingIPOS.csv file
        
        Returns:
            Dict: Upcoming IPO data from CSV
        """
        return await self.read_csv_file('/home/CJSlattery/CSVs/upcomingIPOS.csv')
    
    async def get_recent_ipo_tickers_and_prices(self) -> Dict[str, Any]:
        """
        Get recent IPO tickers and prices from CSV
        
        Returns:
            Dict: Recent IPO tickers and prices data from CSV
        """
        return await self.read_csv_file('/home/CJSlattery/CSVs/recentIPOTickersAndPrices.csv')
    
    async def get_tickers_and_prices(self) -> Dict[str, Any]:
        """
        Get tickers and prices from CSV
        
        Returns:
            Dict: Tickers and prices data from CSV
        """
        return await self.read_csv_file('/home/CJSlattery/CSVs/tickersAndPrices.csv')
    
    async def get_working_rolling(self) -> Dict[str, Any]:
        """
        Get working rolling data from CSV
        
        Returns:
            Dict: Working rolling data from CSV
        """
        return await self.read_csv_file('/home/CJSlattery/CSVs/workingRolling.csv')

    async def get_new_ipo_calendar(self) -> Dict[str, Any]:
        """
        Get the latest IPO calendar snapshot from CSV

        Returns:
            Dict: IPO calendar data from CSV
        """
        return await self.read_csv_file('/home/CJSlattery/CSVs/NewIPOCalendar.csv')
