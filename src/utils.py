import csv
import os
import re
from collections import defaultdict
from datetime import datetime

import psutil

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def remove_header(log_content):
    lines = log_content.split('\n')
    # Look for a more specific header pattern or use a different marker
    header_markers = ['Log File Start', 'BEGIN LOG', '==='] # adjust these markers
    start_index = 0
    for i, line in enumerate(lines):
        if any(marker in line for marker in header_markers):
            start_index = i + 1
            break
    return '\n'.join(lines[start_index:])


def extract_time_range(log_content):
    lines = log_content.split('\n')
    timestamp_pattern = r'(\d{8}/\d{6}\.\d{3})'

    start_time = None
    end_time = None

    # Find the first line with a timestamp
    for line in lines:
        match = re.search(timestamp_pattern, line)
        if match:
            start_time = datetime.strptime(match.group(1), '%Y%m%d/%H%M%S.%f')
            break

    # Find the last line with a timestamp
    for line in reversed(lines):
        match = re.search(timestamp_pattern, line)
        if match:
            end_time = datetime.strptime(match.group(1), '%Y%m%d/%H%M%S.%f')
            break

    if not start_time:
        print("Debug: Unable to extract start time.")
        print("First few lines:", '\n'.join(lines[:5]))
    if not end_time:
        print("Debug: Unable to extract end time.")
        print("Last few lines:", '\n'.join(lines[-5:]))

    return start_time, end_time

def parse_sap_log(log_content):
    jobs = defaultdict(lambda: defaultdict(str))
    reports = defaultdict(dict)
    events = []

    patterns = {
        'timestamp': r'(\d{8}/\d{6}\.\d{3})',
        'message_code': r'(U\d{8})',
        'job_is_to_be_started': r'Job \'(.+?)\' with RunID \'(\d+)\' is to be started\.',
        'job_start': r'Job \'(.+?)\' started with RunID \'(\d+)\'\.',
        'job_end': r'Job \'(.+?)\' with RunID \'(\d+)\' ended with return code \'(\d+)\'.',
        'job_remove': r'Job \'(.+?)\' with RunID \'(\d+)\' has been removed from the job table.',
        'report_start': r'Report \'(\d+)\' for file \'(.+?)\' has been started.',
        'report_end': r'Report \'(\d+)\' ended normally.'
    }

    for line in log_content.split('\n'):
        timestamp_match = re.search(patterns['timestamp'], line)
        message_code_match = re.search(patterns['message_code'], line)

        if timestamp_match and message_code_match:
            timestamp = datetime.strptime(timestamp_match.group(1), '%Y%m%d/%H%M%S.%f')
            message_code = message_code_match.group(1)
            event = line[timestamp_match.end():].strip()

            events.append((timestamp, event, message_code))

            for pattern_name, pattern in patterns.items():
                if pattern_name not in ['timestamp', 'message_code']:
                    match = re.search(pattern, line)
                    if match:
                        if pattern_name == 'job_is_to_be_started':
                            job_name, run_id = match.groups()
                            jobs[run_id].update({
                                'name': job_name,
                                'scheduled_time': timestamp,
                                'scheduled_message_code': message_code
                            })
                        elif pattern_name == 'job_start':
                            job_name, run_id = match.groups()
                            jobs[run_id].update({
                                'name': job_name,
                                'start_time': timestamp,
                                'start_message_code': message_code
                            })
                        elif pattern_name == 'job_end':
                            job_name, run_id, return_code = match.groups()
                            jobs[run_id].update({
                                'name': job_name,
                                'return_code': return_code,
                                'end_message_code': message_code
                            })
                        elif pattern_name == 'job_remove':
                            job_name, run_id = match.groups()
                            jobs[run_id].update({
                                'name': job_name,
                                'end_time': timestamp,
                                'remove_message_code': message_code
                            })
                        elif pattern_name == 'report_start':
                            report_id, file_name = match.groups()
                            reports[report_id] = {
                                'file_name': file_name,
                                'start_time': timestamp,
                                'start_message_code': message_code
                            }
                        elif pattern_name == 'report_end':
                            report_id = match.group(1)
                            if report_id in reports:
                                reports[report_id].update({
                                    'end_time': timestamp,
                                    'end_message_code': message_code
                                })
                        break

    return jobs, reports, events


def save_to_csv(data, filename, headers, mode='w'):
    filepath = os.path.join(PROJECT_ROOT, 'csv', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file_exists = os.path.isfile(filepath)

    with open(filepath, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        if not file_exists or mode == 'w':
            writer.writeheader()
        for key, value in data.items():
            row = {'id': key}
            row.update(value)
            writer.writerow(row)


def save_events_to_csv(events, filename, mode='w'):
    filepath = os.path.join(PROJECT_ROOT, 'csv', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file_exists = os.path.isfile(filepath)

    with open(filepath, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists or mode == 'w':
            writer.writerow(['Timestamp', 'Event', 'Message Code'])
        writer.writerows(events)


def monitor_resources():
    process = psutil.Process()
    return process.cpu_percent(), process.memory_info().rss / (1024 * 1024)  # CPU % and RAM in MB


def save_benchmarks(benchmarks, filename):
    filepath = os.path.join(PROJECT_ROOT, 'benchmarks', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ['File', 'Processing Time (seconds)', 'Peak CPU Usage (%)', 'Peak RAM Usage (MB)', 'Avg CPU Usage (%)',
             'Avg RAM Usage (MB)'])
        writer.writerows(benchmarks)


def read_log_file(log_file_path):
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252', 'ascii']
    for encoding in encodings:
        try:
            with open(log_file_path, 'r', encoding=encoding) as file:
                return file.read()  # Remove the remove_header call
        except UnicodeDecodeError:
            continue
    print(f"Error: Unable to decode file {log_file_path} with any of the attempted encodings.")
    return None

def create_or_clear_csv(filename):
    filepath = os.path.join(PROJECT_ROOT, 'csv', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    open(filepath, 'w').close()  # Create an empty file or clear existing content