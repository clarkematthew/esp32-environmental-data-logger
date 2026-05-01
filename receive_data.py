import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import pandas as pd


HOST = "0.0.0.0"
PORT = 8000
DATA_FILE = "data.csv"
ARCHIVE_FILE = "archive.csv"
HEADER = "Time,Temperature (F),Pressure (hPa),Humidity (%),Gas (KOhms),Altitude (ft)\n"


def ensure_file_exists(path, initial_contents=""):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as file:
            file.write(initial_contents)


def extract_date_string(value):
    parsed = pd.to_datetime(str(value), errors="coerce")
    if pd.notna(parsed):
        return parsed.strftime("%Y-%m-%d")

    return time.strftime("%Y-%m-%d", time.localtime())


def write_data(readings):
    ensure_file_exists(DATA_FILE, HEADER)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    row = ",".join(
        [
            timestamp,
            str(readings["temperature_f"]),
            str(readings["pressure_hpa"]),
            str(readings["humidity_pct"]),
            str(readings["gas_kohms"]),
            str(readings["altitude_ft"]),
        ]
    )

    with open(DATA_FILE, "a", encoding="utf-8") as file:
        file.write(row + "\n")


def archive_data(df, quartile_size, columns):
    quartiles = [
        df.iloc[0:quartile_size],
        df.iloc[quartile_size : 2 * quartile_size],
        df.iloc[2 * quartile_size : 3 * quartile_size],
        df.iloc[3 * quartile_size :],
    ]

    date = extract_date_string(df.tail(1)["Time"].iloc[0])
    archive_lines = ["Date:," + date + "\n"]
    for i, quartile in enumerate(quartiles):
        means = []
        for column in columns:
            if quartile.empty:
                means.append("")
            else:
                means.append(quartile[column].mean())
        archive_lines.append(f"Quartile {i + 1}," + ",".join(map(str, means)) + "\n")

    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, "r", encoding="utf-8") as file:
            existing_contents = file.read()
    else:
        existing_contents = ""

    with open(ARCHIVE_FILE, "w", encoding="utf-8") as file:
        file.writelines(archive_lines)
        file.write(existing_contents)


def reset_data_file_for_new_day(latest_row):
    row_values = [str(value) for value in latest_row.tolist()]
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        file.write(HEADER)
        file.write(",".join(row_values) + "\n")


def archive_if_needed():
    ensure_file_exists(DATA_FILE, HEADER)
    ensure_file_exists(ARCHIVE_FILE)

    df = pd.read_csv(DATA_FILE)
    if df.empty:
        return

    current_date = extract_date_string(df.tail(1)["Time"].iloc[0])
    previous_date = extract_date_string(df.iloc[-2]["Time"]) if len(df) > 1 else current_date

    with open(ARCHIVE_FILE, "r", encoding="utf-8") as file:
        lines = file.readlines()

    archive_date = extract_date_string(lines[0].split(",")[1].strip()) if lines else None
    columns = df.columns[1:]
    quartile_size = max(1, len(df) // 4)

    if current_date != previous_date and current_date != archive_date:
        previous_day_df = df.iloc[:-1].copy()
        if not previous_day_df.empty:
            previous_day_quartile_size = max(1, len(previous_day_df) // 4)
            archive_data(previous_day_df, previous_day_quartile_size, columns)
            reset_data_file_for_new_day(df.iloc[-1])
    elif archive_date is None:
        archive_data(df, quartile_size, columns)


class SensorRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/sensor-data":
            self.send_error(404, "Not found")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        required_fields = {
            "temperature_f",
            "pressure_hpa",
            "humidity_pct",
            "gas_kohms",
            "altitude_ft",
        }
        missing_fields = required_fields - payload.keys()
        if missing_fields:
            self.send_error(400, f"Missing fields: {', '.join(sorted(missing_fields))}")
            return

        write_data(payload)
        archive_if_needed()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')

    def log_message(self, format, *args):
        return


def main():
    ensure_file_exists(DATA_FILE, HEADER)
    ensure_file_exists(ARCHIVE_FILE)

    server = HTTPServer((HOST, PORT), SensorRequestHandler)
    print(f"Listening for sensor data on http://{HOST}:{PORT}/sensor-data")
    server.serve_forever()


if __name__ == "__main__":
    main()
