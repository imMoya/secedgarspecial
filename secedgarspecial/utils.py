import os
import glob
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Union

@dataclass
class Date:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int
        
    def __str__(self):
        return f"{self.year}-{self.month}-{self.day}_{self.hour}-{self.minute}-{self.second}"
    
    @staticmethod
    def from_str(date_str: str) -> Union['Date', None]:
        # Extract the date and time part from the string
        match = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2})', date_str)
        if match:
            date_time_str = match.group(1)
            date, time = date_time_str.split('_')
            year, month, day = date.split('-')
            hour, minute, second = time.split(':')
            return Date(int(year), int(month), int(day), int(hour), int(minute), int(second))
        else:
            return None
    
    @staticmethod
    def from_datetime(dt: datetime):
        return Date(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    
    def to_datetime(self):
        return datetime(self.year, self.month, self.day, self.hour, self.minute, self.second)
    
    def to_file_str(self):
        return f"{self.to_date_str()}_{self.to_time_str()}"
    
    def to_date_str(self):
        return f"{self.year:04}-{self.month:02}-{self.day:02}"
    
    def to_time_str(self):
        return f"{self.hour:02}:{self.minute:02}:{self.second:02}"

class DataManagement:
    def __init__(self, folder: str = "data", html_folder: str = "html_files", latest_default_datestr: str = "2023-01-01_00:00:00"):
        self.folder = folder
        self.html_folder = html_folder
        self.latest_default_datestr = latest_default_datestr
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    @staticmethod
    def get_date_from_filepath(filepath: str) -> str:
        """Extracts the date from a filename of the format 'output_YYYY-MM-DD_HH-MM-SS.json'."""
        match = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})', filepath)
        if match:
            return match.group(1)
        else:
            raise ValueError("No date found in the filename")
        
    @property
    def today(self) -> Date:
        return Date.from_datetime(datetime.now())
    
    @property
    def json_files(self):
        return glob.glob(os.path.join(self.folder, '*.json'))
    
    @property
    def latest_date_before_update(self) -> Date:
        def valid_date_from_str(file):
            try:
                return Date.from_str(file).to_datetime()
            except AttributeError:
                pass
        valid_dates = filter(None, (valid_date_from_str(file) for file in self.json_files))
        latest_file = max(valid_dates, default=None)
        if latest_file is None:
            print(f"Getting files from default initual date {self.latest_default_datestr}")
            return Date.from_str(self.latest_default_datestr)
        else:
            return Date.from_datetime(latest_file)
            
        
        # Extract the date from the latest file
        #latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')
        ##latest_date_str = os.path.basename(latest_file).split('_')[1].split('.')[0]
