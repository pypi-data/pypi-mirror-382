# RegressionTesting
# Copyright (c) 2025 Lionel Guo
# Author: Lionel Guo
# Email: lionelliguo@gmail.com
# GitHub: https://github.com/lionelliguo/regressiontesting

import gspread
from google.oauth2.service_account import Credentials
import subprocess
import json
import re
import time
from datetime import datetime

class RegressionTesting:
    def __init__(self, spreadsheet_url, service_account_file, sleep_seconds=1.0, ignore_case=True, output_batch_size=0, copy_batch_size=0):
        self.spreadsheet_url = spreadsheet_url
        self.service_account_file = service_account_file
        self.sleep_seconds = sleep_seconds
        self.ignore_case = ignore_case
        self.output_batch_size = output_batch_size
        self.copy_batch_size = copy_batch_size

        SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(self.service_account_file, scopes=SCOPES)
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open_by_url(self.spreadsheet_url)

    def load_config_rules(self):
        try:
            config_sheet = self.spreadsheet.worksheet("CONFIG")
        except Exception:
            print("CONFIG sheet not found. Using empty rules.")
            return [], [], []

        config_header = config_sheet.row_values(1)
        config_index = {name: i for i, name in enumerate(config_header) if name}
        col_num1 = config_index.get("SELECTION_RULE_1")
        col_num2 = config_index.get("SELECTION_RULE_2")
        col_comp = config_index.get("COMPARISON_RULE")

        SELECTION_RULE_1 = []
        SELECTION_RULE_2 = []
        COMPARISON_RULE = []

        values = config_sheet.get_all_values()
        for row in values[1:]:
            if col_num1 is not None and col_num1 < len(row):
                val1 = row[col_num1].strip()
                if val1:
                    SELECTION_RULE_1.append(val1)
            if col_num2 is not None and col_num2 < len(row):
                val2 = row[col_num2].strip()
                if val2:
                    SELECTION_RULE_2.append(val2)
            if col_comp is not None and col_comp < len(row):
                valc = row[col_comp].strip()
                if valc:
                    COMPARISON_RULE.append(valc)
        
        print("Loaded CONFIG rules:")
        print("SELECTION_RULE_1:", SELECTION_RULE_1)
        print("SELECTION_RULE_2:", SELECTION_RULE_2)
        print("COMPARISON_RULE:", COMPARISON_RULE)

        return SELECTION_RULE_1, SELECTION_RULE_2, COMPARISON_RULE

    def run_curl_and_get_headers(self, curl_cmd, exclude_headers=None):
        if not curl_cmd or not curl_cmd.strip().startswith("curl"):
            return None

        exclude_list = exclude_headers if exclude_headers else []

        try:
            completed = subprocess.run(
                curl_cmd + " -s -i", shell=True, capture_output=True, text=True, timeout=30
            )
            response_text = completed.stdout or ""
        except Exception as e:
            return json.dumps({"error": f"curl failed: {str(e)}"}, ensure_ascii=False)

        parts = re.split(r"\r\n\r\n|\n\n", response_text, maxsplit=1)
        header_lines = parts[0].splitlines() if parts else []
        if not header_lines:
            return json.dumps({"error": "No response headers"}, ensure_ascii=False)

        status_line = header_lines[0].strip()
        status_parts = status_line.split(" ", 2)
        http_version = status_parts[0] if len(status_parts) > 0 else ""
        status_code = int(status_parts[1]) if len(status_parts) > 1 and status_parts[1].isdigit() else None
        status_message = status_parts[2] if len(status_parts) > 2 else ""

        headers = {}
        for line in header_lines[1:]:
            if ": " in line:
                k, v = line.split(": ", 1)
            elif ":" in line:
                k, v = line.split(":", 1)
            else:
                continue
            if k.strip() in exclude_list:
                continue
            headers[k.strip()] = v.strip()

        return json.dumps({
            "http_version": http_version,
            "status_code": status_code,
            "status_message": status_message,
            "headers": headers
        }, ensure_ascii=False, indent=2)
    
    def parse_json_to_obj(self, s):
        """Safely parse JSON string into Python dict."""
        if not s:
            return {}
        try:
            return json.loads(s)
        except Exception:
            return {"__raw": s}

    def col_letter(self, idx):
        """Convert 0-based column index to Excel-style letter."""
        return chr(65 + idx)

def process_sheet(sheet, selection_rule_1, selection_rule_2, comparison_rule):
    """Process main sheet, run CURL, store results, compare headers, batch update."""
    header = sheet.row_values(1)
    col_index = {name: i for i, name in enumerate(header) if name}

    required_cols = ["CURL_1", "RESULT_1", "CURL_2", "RESULT_2", "STATUS"]
    missing = [c for c in required_cols if c not in col_index]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    all_values = sheet.get_all_values()
    num_rows = len(all_values)

    result1_list = []
    result2_list = []
    status_list = []
    processed_rows = set()  # Set to keep track of processed rows

    # Ensure comparison rules are in lowercase if case-insensitive comparison is enabled
    if IGNORE_CASE:
        comparison_rule = [rule.lower() for rule in comparison_rule]

    for idx, row in enumerate(all_values[1:], start=2):
        curl1 = row[col_index["CURL_1"]] if col_index["CURL_1"] < len(row) else ""
        curl2 = row[col_index["CURL_2"]] if col_index["CURL_2"] < len(row) else ""

        result1 = run_curl_and_get_headers(curl1, selection_rule_1) if curl1 else ""
        result2 = run_curl_and_get_headers(curl2, selection_rule_2) if curl2 else ""

        parsed1 = parse_json_to_obj(result1)
        parsed2 = parse_json_to_obj(result2)

        headers1 = parsed1.get("headers", {})
        headers2 = parsed2.get("headers", {})

        http_version_1 = parsed1.get("http_version")
        http_version_2 = parsed2.get("http_version")
        status_code_1 = parsed1.get("status_code")
        status_code_2 = parsed2.get("status_code")
        status_message_1 = parsed1.get("status_message")
        status_message_2 = parsed2.get("status_message")

        # Ignore comparison rule headers case-sensitively based on the global IGNORE_CASE variable
        if IGNORE_CASE:
            # Convert header keys to lowercase for comparison
            headers1_filtered = {k.lower(): v for k, v in headers1.items() if k.lower() not in comparison_rule}
            headers2_filtered = {k.lower(): v for k, v in headers2.items() if k.lower() not in comparison_rule}

            # Compare also top-level fields unless excluded by COMPARISON_RULE
            if "http_version" not in comparison_rule:
                headers1_filtered["http_version"] = http_version_1
                headers2_filtered["http_version"] = http_version_2
            if "status_code" not in comparison_rule:
                headers1_filtered["status_code"] = status_code_1
                headers2_filtered["status_code"] = status_code_2
            if "status_message" not in comparison_rule:
                headers1_filtered["status_message"] = status_message_1
                headers2_filtered["status_message"] = status_message_2
        else:
            # Directly compare header keys without converting to lowercase
            headers1_filtered = {k: v for k, v in headers1.items() if k not in comparison_rule}
            headers2_filtered = {k: v for k, v in headers2.items() if k not in comparison_rule}

            if "http_version" not in comparison_rule:
                headers1_filtered["http_version"] = http_version_1
                headers2_filtered["http_version"] = http_version_2
            if "status_code" not in comparison_rule:
                headers1_filtered["status_code"] = status_code_1
                headers2_filtered["status_code"] = status_code_2
            if "status_message" not in comparison_rule:
                headers1_filtered["status_message"] = status_message_1
                headers2_filtered["status_message"] = status_message_2

        # Compare headers + top-level fields
        status = "PASS" if headers1_filtered == headers2_filtered else "FAIL"

        result1_list.append([result1])
        result2_list.append([result2])
        status_list.append([status])

        # If OUTPUT_BATCH_SIZE > 0, output in batches
        if OUTPUT_BATCH_SIZE > 0 and len(result1_list) >= OUTPUT_BATCH_SIZE:
            batch_update(sheet, col_index, result1_list, result2_list, status_list, idx - len(result1_list) + 1)
            result1_list, result2_list, status_list = [], [], []  # Reset after batch update

    # If there are remaining results to be updated
    if result1_list:
        batch_update(sheet, col_index, result1_list, result2_list, status_list, num_rows - len(result1_list) + 1)

    def batch_update(self, sheet, col_index, result1_list, result2_list, status_list, start_row):
        num_rows = len(result1_list)
        end_row = start_row + num_rows - 1
        sheet.update(values=result1_list, range_name=f"{self.col_letter(col_index['RESULT_1'])}{start_row}:{self.col_letter(col_index['RESULT_1'])}{end_row}")
        sheet.update(values=result2_list, range_name=f"{self.col_letter(col_index['RESULT_2'])}{start_row}:{self.col_letter(col_index['RESULT_2'])}{end_row}")
        sheet.update(values=status_list, range_name=f"{self.col_letter(col_index['STATUS'])}{start_row}:{self.col_letter(col_index['STATUS'])}{end_row}")

        print(f"Batch updated {num_rows} rows from {start_row} to {end_row}.")

        for i, status in enumerate(status_list, start=start_row):
            print(f"Row {i} STATUS: {status[0]}")

    def create_new_sheet_with_current_datetime(self):
        current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M")
        try:
            new_sheet = self.spreadsheet.add_worksheet(title=current_datetime, rows="100", cols="100")
            print(f"New sheet created: {current_datetime}")

            # Copy content from the 'TEST CASE' sheet
            try:
                test_case_sheet = self.spreadsheet.worksheet("TEST CASE")
            except Exception:
                print("TEST CASE sheet not found.")
                return None
            
            if self.copy_batch_size == 0:
                values = test_case_sheet.get_all_values()
                new_sheet.insert_rows(values, 1)
                print(f"All rows copied from TEST CASE to {current_datetime}")
            else:
                all_values = test_case_sheet.get_all_values()
                num_rows = len(all_values)
                batch_size = self.copy_batch_size
                for start_row in range(1, num_rows + 1, batch_size):
                    end_row = min(start_row + batch_size - 1, num_rows)
                    batch_values = all_values[start_row - 1:end_row]
                    new_sheet.insert_rows(batch_values, start_row)
                    print(f"Copied rows {start_row} to {end_row} from TEST CASE.")

            return new_sheet

        except Exception as e:
            print(f"Failed to create new sheet: {str(e)}")
            return None
        