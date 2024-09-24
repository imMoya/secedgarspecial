import os
import time
import secedgarspecial as sec


if __name__ == "__main__":
    dm = sec.DataManagement(folder="oddlots", html_folder="oddlots_html")
    # File output paths
    latest_date_file = os.path.join(dm.folder, f"output_{dm.latest_date_before_update.to_file_str()}.json")
    today_date_file = os.path.join(dm.folder, f"output_{dm.today.to_file_str()}.json")
    html_mapper_file = os.path.join(dm.folder, "html_mapper.json")
    join_html_mapper = os.path.join(dm.folder, f"join_html_mapper_{dm.today.to_date_str()}.json")
    # Run the text search command
    command = (
        f'poetry run '
        f'edgar-tool text_search odd lots '
        f'--start_date "{dm.latest_date_before_update.to_date_str()}" --end_date "{dm.today.to_date_str()}" '
        f'--output "{today_date_file}"'
    )
    print(command)
    os.system(command)
    sec.JsonHandler(latest_date_file, today_date_file).read_and_combine(html_mapper_file, filter="005-", filter_field="file_num")
    #join_html_mapper = "data/join_html_mapper.json"
    #sec.JsonHandler(latest_date_file, latest_date_file).join_ticker_json(html_mapper_file, join_html_mapper)
    # HTML Download
    html_handler = sec.HTMLHandler(dm.html_folder).download_html_files(sec.JsonHandler.read_json_file(html_mapper_file))

    #### SPIN OFFS
    dm = sec.DataManagement(folder="spinoffs", html_folder="spinoffs_html")
    # File output paths
    latest_date_file = os.path.join(dm.folder, f"output_{dm.latest_date_before_update.to_file_str()}.json")
    today_date_file = os.path.join(dm.folder, f"output_{dm.today.to_file_str()}.json")
    html_mapper_file = os.path.join(dm.folder, "html_mapper.json")
    join_html_mapper = os.path.join(dm.folder, f"join_html_mapper_{dm.today.to_date_str()}.json")
    # Run the text search command
    command = (
        f'poetry run '
        f'edgar-tool text_search the '
        f'--start_date "{dm.latest_date_before_update.to_date_str()}" --end_date "{dm.today.to_date_str()}" '
        f'--single_forms "[\'10-12B\']" '
        f'--output "{today_date_file}"'
    )
    print(command)
    os.system(command)
    sec.JsonHandler(latest_date_file, today_date_file).read_and_combine(html_mapper_file, filter="ex991", filter_field="filing_document_url")