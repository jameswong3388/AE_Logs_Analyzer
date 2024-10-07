import os
import re
import time
from collections import defaultdict
from datetime import datetime

import csv

# Define the project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def remove_header(log_content):
    lines = log_content.split('\n')
    for i, line in enumerate(lines):
        if 'U02000071' in line:
            return '\n'.join(lines[i:])
    return log_content  # Return original content if U02000071 is not found


def parse_sap_log(log_content):
    # Remove header
    log_content = remove_header(log_content)

    # Regular expressions for parsing
    timestamp_pattern = r'(\d{8}/\d{6}\.\d{3})'
    message_code_pattern = r'(U\d{8})'
    job_is_to_be_started_pattern = r'Job \'(.+?)\' with RunID \'(\d+)\' is to be started\.'
    job_start_pattern = r'Job \'(.+?)\' started with RunID \'(\d+)\'\.'
    job_end_pattern = r'Job \'(.+?)\' with RunID \'(\d+)\' ended with return code \'(\d+)\'.'
    job_remove_pattern = r'Job \'(.+?)\' with RunID \'(\d+)\' has been removed from the job table.'
    report_start_pattern = r'Report \'(\d+)\' for file \'(.+?)\' has been started.'
    report_end_pattern = r'Report \'(\d+)\' ended normally.'

    # Data structures to store parsed information
    jobs = defaultdict(lambda: defaultdict(str))
    reports = defaultdict(dict)
    events = []

    # Parse the log line by line
    for line in log_content.split('\n'):
        timestamp_match = re.search(timestamp_pattern, line)
        message_code_match = re.search(message_code_pattern, line)

        if timestamp_match and message_code_match:
            timestamp = datetime.strptime(timestamp_match.group(1), '%Y%m%d/%H%M%S.%f')
            message_code = message_code_match.group(1)
            event = line[timestamp_match.end():].strip()  # Extract everything after the timestamp as the event

            # Add each line as an event
            events.append((timestamp, event, message_code))

            # Check for job is to be started
            job_is_to_be_started_match = re.search(job_is_to_be_started_pattern, line)
            if job_is_to_be_started_match:
                job_name, run_id = job_is_to_be_started_match.groups()
                jobs[run_id].update({
                    'name': job_name,
                    'scheduled_time': timestamp,
                    'scheduled_message_code': message_code
                })

            # Check for job start
            job_start_match = re.search(job_start_pattern, line)
            if job_start_match:
                job_name, run_id = job_start_match.groups()
                jobs[run_id].update({
                    'name': job_name,
                    'start_time': timestamp,
                    'start_message_code': message_code
                })

            # Check for job end (update return code)
            job_end_match = re.search(job_end_pattern, line)
            if job_end_match:
                job_name, run_id, return_code = job_end_match.groups()
                jobs[run_id].update({
                    'name': job_name,
                    'return_code': return_code,
                    'end_message_code': message_code
                })

            # Check for job removal (use as job end)
            job_remove_match = re.search(job_remove_pattern, line)
            if job_remove_match:
                job_name, run_id = job_remove_match.groups()
                jobs[run_id].update({
                    'name': job_name,
                    'end_time': timestamp,
                    'remove_message_code': message_code
                })

            # Check for report start
            report_start_match = re.search(report_start_pattern, line)
            if report_start_match:
                report_id, file_name = report_start_match.groups()
                reports[report_id] = {
                    'file_name': file_name,
                    'start_time': timestamp,
                    'start_message_code': message_code
                }

            # Check for report end
            report_end_match = re.search(report_end_pattern, line)
            if report_end_match:
                report_id = report_end_match.group(1)
                if report_id in reports:
                    reports[report_id]['end_time'] = timestamp
                    reports[report_id]['end_message_code'] = message_code

    return jobs, reports, events

def save_to_csv(data, filename, headers):
    filepath = os.path.join(PROJECT_ROOT, 'csv', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for key, value in data.items():
            row = {'id': key}
            row.update(value)
            writer.writerow(row)

def save_events_to_csv(events, filename):
    filepath = os.path.join(PROJECT_ROOT, 'csv', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Timestamp', 'Event', 'Message Code'])
        writer.writerows(events)

def process_log_to_csv(log_file_path):
    start_time = time.time()

    # List of encodings to try
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252', 'ascii']

    log_content = None
    for encoding in encodings:
        try:
            with open(log_file_path, 'r', encoding=encoding) as file:
                log_content = file.read()
            break  # If successful, break out of the loop
        except UnicodeDecodeError:
            continue  # Try the next encoding

    if log_content is None:
        print(f"Error: Unable to decode file {log_file_path} with any of the attempted encodings.")
        return

    # Parse the log
    jobs, reports, events = parse_sap_log(log_content)

    # Save jobs to CSV
    job_headers = ['id', 'name', 'scheduled_time', 'start_time', 'end_time', 'return_code',
                   'scheduled_message_code', 'start_message_code', 'end_message_code', 'remove_message_code']
    save_to_csv(jobs, 'jobs.csv', job_headers)

    # Save reports to CSV
    report_headers = ['id', 'file_name', 'start_time', 'end_time', 'start_message_code', 'end_message_code']
    save_to_csv(reports, 'reports.csv', report_headers)

    # Save events to CSV
    save_events_to_csv(events, 'events.csv')

    end_time = time.time()
    processing_time = end_time - start_time

    print(f"Data has been saved to csv/jobs.csv, csv/reports.csv, and csv/events.csv")
    print(f"Processing time: {processing_time:.2f} seconds")

    # Save processing time to CSV
    processing_time_path = os.path.join(PROJECT_ROOT, 'csv', 'processing_time.csv')
    os.makedirs(os.path.dirname(processing_time_path), exist_ok=True)
    with open(processing_time_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['File', 'Processing Time (seconds)'])
        writer.writerow([log_file_path, processing_time])

    print("Processing time has been saved to csv/processing_time.csv")

if __name__ == "__main__":
    log_file_path = os.path.join(PROJECT_ROOT, 'logs', '158174833.LOG.txt')
    process_log_to_csv(log_file_path)