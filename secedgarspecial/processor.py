import os
from secedgarspecial import *

class SECDataProcessor:
    def __init__(self, folder, html_folder, search_term, filters, filter_field, forms=None):
        self.dm = DataManagement(folder=folder, html_folder=html_folder)
        self.search_term = search_term
        self.filters = filters
        self.filter_field = filter_field
        self.forms = forms

        # File output paths
        self.latest_date_file = os.path.join(self.dm.folder, f"output_{self.dm.latest_date_before_update.to_file_str()}.json")
        self.today_date_file = os.path.join(self.dm.folder, f"output_{self.dm.today.to_file_str()}.json")
        self.html_mapper_file = os.path.join(self.dm.folder, "html_mapper.json")
        self.join_html_mapper = os.path.join(self.dm.folder, "join_html_mapper.json")

    def build_command(self):
        # Construct the text search command
        forms_clause = f'--single_forms "{self.forms}" ' if self.forms else ""
        command = (
            f'poetry run edgar-tool text_search {self.search_term} '
            f'--start_date "{self.dm.latest_date_before_update.to_date_str()}" '
            f'--end_date "{self.dm.today.to_date_str()}" '
            f'{forms_clause}--output "{self.today_date_file}"'
        )
        return command

    def execute_search_command(self):
        command = self.build_command()
        print(command)
        try:
            os.system(command)
            JsonHandler(self.latest_date_file, self.today_date_file).read_and_combine(
                self.html_mapper_file, filter=self.filters, filter_field=self.filter_field
            )
        except Exception:
            print(f"No data to update for {self.search_term}")

    def join_by_ticker(self):
        JsonHandler().join_ticker_json(self.html_mapper_file, self.join_html_mapper)

    def download_html_files(self):
        html_handler = HTMLHandler(self.dm.html_folder)
        html_data = JsonHandler.read_json_file(self.html_mapper_file)
        html_handler.download_html_files(html_data)

    def run(self):
        self.execute_search_command()
        self.join_by_ticker()
        self.download_html_files()