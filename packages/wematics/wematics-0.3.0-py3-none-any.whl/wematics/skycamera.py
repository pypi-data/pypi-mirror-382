import requests
import os
import re
import datetime
from tqdm import tqdm
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo


import requests
import os
import re
import datetime
from tqdm import tqdm
from zoneinfo import ZoneInfo

class Skycamera:
    def __init__(self, api_key):
        self.base_url = "http://wematics.cloud"
        self.api_key = api_key

    def _make_request(self, endpoint: str, params=None):
        """Makes a request to the API with error handling."""
        url = f"{self.base_url}{endpoint}"
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        print(url)
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def list_cameras(self):
        """Lists all available cameras for the user."""
        return self._make_request("/cameras")

    def list_variables(self, camera):
        """Lists all available variables for a given camera."""
        return self._make_request(f"/{camera}/variables")

    def list_dates(self, camera, variable):
        """Lists all available dates for a given camera and variable."""
        return self._make_request(f"/{camera}/dates/{variable}")

    def list_files(self, camera, variable, date, timezone='local'):
        """Lists all available files for a given camera, variable, and date."""
        params = {'timezone': timezone}
        return self._make_request(f"/{camera}/files/{variable}/{date}", params)

    def download_file(self, camera, variable, file_name, download_path="", timezone='local'):
        """Downloads a single file."""
        params = {'timezone': timezone}
        url = f"{self.base_url}/{camera}/download/{variable}/{file_name}"
        self._download_file(url, os.path.basename(file_name), download_path, params)

    def _download_file(self, url, file_name, download_path="", params=None):
        """Downloads a file from a given URL (helper function)."""
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        response = requests.get(url, params=params, stream=True)

        if response.status_code == 200:
            file_path = os.path.join(download_path, file_name)
            total_size = int(response.headers.get('content-length', 0))

            with open(file_path, 'wb') as f:
                for chunk in tqdm(response.iter_content(chunk_size=4096), 
                                total=total_size // 4096, 
                                unit='KB', 
                                desc=f"Downloading {file_name}"):
                    if chunk:
                        f.write(chunk)
        else:
            print(f"Error downloading {file_name}: {response.text}")

    def _parse_input_datetime(self, dt_string):
        """Parse input datetime string in expected format YYYY-MM-DD_HH_MM_SS."""
        try:
            match = re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}_\d{2}_\d{2})", dt_string)
            if not match:
                raise ValueError(f"Invalid datetime format: {dt_string}. Expected YYYY-MM-DD_HH_MM_SS")
            return datetime.datetime.strptime(match.group(1), "%Y-%m-%d_%H_%M_%S")
        except ValueError as e:
            raise ValueError(f"Could not parse datetime '{dt_string}': {e}")

    def _parse_filename_datetime(self, filename, timezone_mode='local'):
        """
        Parse datetime from various filename formats.
        Returns datetime object or None if parsing fails.
        """
        # Remove file extensions for parsing
        base_name = filename.replace('.webp', '').replace('.csv', '').replace('.jpg', '').replace('.png', '')
        
        # Format 1: ISO with timezone offset - 2025-08-19T00-00-28+02-00_exp55000ms_0000
        match = re.search(r"(\d{4}-\d{2}-\d{2})T(\d{2})-(\d{2})-(\d{2})([+-])(\d{2})-(\d{2})", base_name)
        if match:
            try:
                date_part = match.group(1)      # 2025-08-19
                hour = match.group(2)           # 00
                minute = match.group(3)         # 00
                second = match.group(4)         # 28
                tz_sign = match.group(5)        # + or -
                tz_hour = int(match.group(6))   # 02
                tz_min = int(match.group(7))    # 00
                
                # Create datetime
                dt = datetime.datetime.strptime(f"{date_part} {hour}:{minute}:{second}", "%Y-%m-%d %H:%M:%S")
                
                # Apply timezone offset if requesting UTC
                if timezone_mode == 'utc':
                    offset_minutes = (tz_hour * 60 + tz_min)
                    if tz_sign == '+':
                        dt = dt - datetime.timedelta(minutes=offset_minutes)
                    else:
                        dt = dt + datetime.timedelta(minutes=offset_minutes)
                
                return dt
            except ValueError:
                pass
        
        # Format 2: Standard underscore format - 2025-08-19_13_00_00
        match = re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}_\d{2}_\d{2})", base_name)
        if match:
            try:
                return datetime.datetime.strptime(match.group(1), "%Y-%m-%d_%H_%M_%S")
            except ValueError:
                pass
        
        # Format 3: ISO standard with colons - 2025-08-19T13:00:00
        match = re.search(r"(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2}):(\d{2})", base_name)
        if match:
            try:
                return datetime.datetime.strptime(match.group(0), "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                pass
        
        # Format 4: ISO with microseconds - 2025-08-19T13:00:00.123
        match = re.search(r"(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2}):(\d{2})\.(\d+)", base_name)
        if match:
            try:
                return datetime.datetime.strptime(match.group(0)[:19], "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                pass
        
        # Could not parse - return None
        return None

    def download_files_in_range(self, camera, variable, start_datetime, end_datetime, download_path=".", timezone='local'):
        """
        Downloads files for a camera and variable within a datetime range.
        
        Args:
            camera: Camera name
            variable: Variable name (HDR, RGB, etc.)
            start_datetime: Start time in format YYYY-MM-DD_HH_MM_SS
            end_datetime: End time in format YYYY-MM-DD_HH_MM_SS  
            download_path: Directory to save files
            timezone: 'local' or 'utc'
        
        Returns:
            List of downloaded filenames
        """
        
        # Parse and validate input datetimes
        try:
            start_dt = self._parse_input_datetime(start_datetime)
            end_dt = self._parse_input_datetime(end_datetime)
        except ValueError as e:
            print(f"Error: {e}")
            return []
        
        if start_dt >= end_dt:
            print(f"Error: Start datetime ({start_dt}) must be before end datetime ({end_dt})")
            return []
        
        # Extract date range
        start_date = start_dt.date()
        end_date = end_dt.date()
        
        print(f"Searching for files from {start_dt} to {end_dt} in {timezone} timezone")
        
        # Collect all files from the date range
        all_files = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            try:
                response = self.list_files(camera, variable, date_str, timezone)
                if 'files' in response:
                    day_files = response['files']
                    all_files.extend(day_files)
                    print(f"Found {len(day_files)} files for {date_str}")
            except Exception as e:
                print(f"No files available for {date_str}: {e}")
            
            current_date += datetime.timedelta(days=1)
        
        if not all_files:
            print(f"No files found for date range {start_date} to {end_date}")
            return []
        
        print(f"Total files found: {len(all_files)}")
        
        # Filter files by datetime range
        filtered_files = []
        parsing_errors = 0
        
        for filename in all_files:
            file_dt = self._parse_filename_datetime(filename, timezone)
            
            if file_dt is None:
                parsing_errors += 1
                continue
            
            # Check if file datetime is within range (inclusive bounds)
            if start_dt <= file_dt <= end_dt:
                filtered_files.append(filename)
        
        print(f"Files matching time range: {len(filtered_files)}")
        if parsing_errors > 0:
            print(f"Files with unparseable names: {parsing_errors}")
        
        if not filtered_files:
            print(f"No files found in the specified time range {start_datetime} to {end_datetime}")
            if parsing_errors > 0:
                print(f"Note: {parsing_errors} files were skipped due to unrecognized filename formats")
                # Show sample filenames to help debug
                sample_files = all_files[:3]
                print(f"Sample filenames: {sample_files}")
            return []
        
        # Create download directory if it doesn't exist
        if download_path and not os.path.exists(download_path):
            os.makedirs(download_path)
        
        print(f"Downloading {len(filtered_files)} files...")
        
        # Download filtered files
        for filename in tqdm(filtered_files, desc="Downloading", unit="file"):
            try:
                self.download_file(camera, variable, filename, download_path, timezone)
            except Exception as e:
                print(f"Error downloading {filename}: {e}")
        
        return filtered_files