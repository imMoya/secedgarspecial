import os
import string
import json
from typing import Union, List, Dict, Optional

class JsonHandler:
    def __init__(self, json_orig: Optional[str] = None, json_new: Optional[str] = None):
        self.json_orig = json_orig
        self.json_new = json_new
   
    @staticmethod
    def read_json_file(file_path: str) -> Union[List, Dict]:
        """Read JSON data from a file."""
        with open(file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def write_json_file(file_path: str, data: Union[List, Dict]) -> None:
        """Write JSON data to a file."""
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def combine_json_data(data1: Union[List, Dict], data2: Union[List, Dict]) -> Union[List, Dict]:
        """Combine two JSON data structures."""
        if isinstance(data1, list) and isinstance(data2, list):
            return data1 + data2  # Concatenate lists
        elif isinstance(data1, dict) and isinstance(data2, dict):
            combined_data = {**data1, **data2}  # Merge dictionaries
            return combined_data
        else:
            raise ValueError("Both JSON data structures must be of the same type (both lists or both dictionaries)")
    
    @staticmethod
    def combine_json_data_(data1: Union[List, Dict], data2: Union[List, Dict]) -> Union[List, Dict]:
        """Combine two JSON data structures without duplicates."""
        if isinstance(data1, list) and isinstance(data2, list):
            combined_data = data1.copy()
            seen = {json.dumps(entry, sort_keys=True) for entry in data1}
            for entry in data2:
                entry_str = json.dumps(entry, sort_keys=True)
                if entry_str not in seen:
                    combined_data.append(entry)
                    seen.add(entry_str)
            return combined_data
        elif isinstance(data1, dict) and isinstance(data2, dict):
            combined_data = data1.copy()
            for key, value in data2.items():
                if key not in combined_data:
                    combined_data[key] = value
            return combined_data
        else:
            raise ValueError("Both JSON data structures must be of the same type (both lists or both dictionaries)")
    
    def read_and_combine(self, html_mapper_file: str, filter: Optional[str]= None, filter_field: Optional[List[str]]= None) -> None:
        """Read and combine the original and new json data"""
        
        if self.is_file_empty(self.json_new) == True:
            os.rename(self.json_orig, self.json_new)
            return
        
        data_new = self.read_json_file(self.json_new)
        
        try:
            data_orig = self.read_json_file(self.json_orig)
            data = self.combine_json_data_(data_orig, data_new)
        except (ValueError, FileNotFoundError):
            data = data_new
        
        if filter:
            filtered_data = [
                entry for entry in data
                if 'file_num' in entry and any(f in entry[filter_field] for f in filter)
                #if 'form_name' in entry and filter.lower() in entry['form_name'].lower()
            ]
            self.write_json_file(self.json_new, filtered_data)
            self.write_json_file(
                html_mapper_file, self.extract_data_for_html(filtered_data)
            )
        else:
            self.write_json_file(self.json_new, data)
            self.write_json_file(
                html_mapper_file, self.extract_data_for_html(data)
            )
        
        if self.is_file_empty(self.json_new) == True:
            os.remove(self.json_new)
            os.rename(self.json_orig, self.json_new)
        else:
            try:
                os.remove(self.json_orig)            
            except FileNotFoundError:
                pass
    
    def extract_data_for_html(self, data: List[dict]):
        extracted_data = []
        for item in data:
            ticker = item.get('ticker', [])
            if isinstance(ticker, str):
                ticker = ticker.split(",")[0].strip()
            else:
                name = item.get('entity_name', [])
                ticker = name.translate(str.maketrans('', '', string.punctuation)).replace(" ", "").upper()
            
            filed_at = item.get('filed_at')
            file_num = item.get('file_num')
            url = item.get('filing_document_url', [])
            if isinstance(url, list):
                url = url[0] if ticker else None
            if ticker and filed_at and file_num and url:
                extracted_data.append({
                    'id': f'{ticker}_{file_num}_{filed_at}.html',
                    'ticker_id': ticker,
                    'ticker': self.ticker_str_to_list(ticker),
                    'url': url,
                    'num_filing': file_num,
                    'date_filing': filed_at,
                })
        return extracted_data
    
    @staticmethod
    def ticker_str_to_list(ticker: Union[str, None]) -> Union[List[str], None]:
        """Convert ticker string to a list."""
        ticker_list = []
        if ticker:
            if ', ' in ticker:
                elements = [element.strip() for element in ticker.split(',')]
                ticker_list.extend(elements)
            else:
                ticker_list = [ticker]
            return ticker_list
        else:
            return None
        
    @staticmethod
    def is_file_empty(file: str) -> bool:
        """Check if file is empty (contains just '[]')"""
        if os.path.exists(file):
            with open(file, 'r') as f:
                content = f.read().strip() 
                if content == '[]':
                    return True
                else:
                    return False
        else:
            print(f"File '{file}' does not exist.")
    
    def join_ticker_json(self, html_mapper_file: str, output_file: str):
        """Read the html_mapper_file and group the data by ticker."""
        data = self.read_json_file(html_mapper_file)
        grouped_data = {}
        for entry in data:
            ticker_id = entry['ticker_id']
            if ticker_id not in grouped_data:
                grouped_data[ticker_id] = {'ticker': [], 'urls': [], 'nums_filing': [], 'dates_filing': []}   
            if entry['ticker'] not in grouped_data[ticker_id]['ticker']:
                grouped_data[ticker_id]['ticker'].append(entry['ticker'])         
            grouped_data[ticker_id]['urls'].append(entry['url'])
            grouped_data[ticker_id]['nums_filing'].append(entry['num_filing'])
            grouped_data[ticker_id]['dates_filing'].append(entry['date_filing'])
        self.write_json_file(output_file, grouped_data)
