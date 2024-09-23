import os
import time
import secedgarspecial as sec


if __name__ == "__main__":
    dm = sec.DataManagement()
    # File output paths
    latest_date_file = os.path.join(dm.folder, f"output_{dm.latest_date_before_update.to_file_str()}.json")
    today_date_file = os.path.join(dm.folder, f"output_{dm.today.to_file_str()}.json")
    html_mapper_file = os.path.join(dm.folder, "html_mapper.json")
    join_html_mapper = os.path.join(dm.folder, f"join_html_mapper_{dm.today.to_date_str()}.json")
    # Run the text search command
    date1 = sec.Date(2023, 5, 7, 12, 56, 58)
    date2 = sec.Date(2024, 5, 30, 12, 56, 58)
    date3 = sec.Date(2024, 9, 7, 12, 56, 58)
    command = (
        f'poetry run '
        f'edgar-tool text_search odd lots '
        f'--start_date "{dm.latest_date_before_update.to_date_str()}" --end_date "{dm.today.to_date_str()}" '
        f'--output "{today_date_file}"'
    )
    print(command)
    os.system(command)
    sec.JsonHandler(latest_date_file, today_date_file).read_and_combine(html_mapper_file, filter="005-")
