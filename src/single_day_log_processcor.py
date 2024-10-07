import re
import csv
from datetime import datetime
from collections import defaultdict


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

            # Check for job is to be started
            job_is_to_be_started_match = re.search(job_is_to_be_started_pattern, line)
            if job_is_to_be_started_match:
                job_name, run_id = job_is_to_be_started_match.groups()
                jobs[run_id].update({
                    'name': job_name,
                    'scheduled_time': timestamp,
                    'scheduled_message_code': message_code
                })
                events.append((timestamp, f"Job {job_name} (RunID: {run_id}) is to be started", message_code))

            # Check for job start
            job_start_match = re.search(job_start_pattern, line)
            if job_start_match:
                job_name, run_id = job_start_match.groups()
                jobs[run_id].update({
                    'name': job_name,
                    'start_time': timestamp,
                    'start_message_code': message_code
                })
                events.append((timestamp, f"Job {job_name} (RunID: {run_id}) started", message_code))

            # Check for job end (update return code)
            job_end_match = re.search(job_end_pattern, line)
            if job_end_match:
                job_name, run_id, return_code = job_end_match.groups()
                jobs[run_id].update({
                    'name': job_name,
                    'return_code': return_code,
                    'end_message_code': message_code
                })
                events.append((timestamp, f"Job {job_name} (RunID: {run_id}) ended with return code {return_code}", message_code))

            # Check for job removal (use as job end)
            job_remove_match = re.search(job_remove_pattern, line)
            if job_remove_match:
                job_name, run_id = job_remove_match.groups()
                jobs[run_id].update({
                    'name': job_name,
                    'end_time': timestamp,
                    'remove_message_code': message_code
                })
                events.append((timestamp, f"Job {job_name} (RunID: {run_id}) removed from job table", message_code))

            # Check for report start
            report_start_match = re.search(report_start_pattern, line)
            if report_start_match:
                report_id, file_name = report_start_match.groups()
                reports[report_id] = {
                    'file_name': file_name,
                    'start_time': timestamp,
                    'start_message_code': message_code
                }
                events.append((timestamp, f"Report {report_id} started for file {file_name}", message_code))

            # Check for report end
            report_end_match = re.search(report_end_pattern, line)
            if report_end_match:
                report_id = report_end_match.group(1)
                if report_id in reports:
                    reports[report_id]['end_time'] = timestamp
                    reports[report_id]['end_message_code'] = message_code
                events.append((timestamp, f"Report {report_id} ended normally", message_code))

    return jobs, reports, events


def save_to_csv(data, filename, headers):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for key, value in data.items():
            row = {'id': key}
            row.update(value)
            writer.writerow(row)


def save_events_to_csv(events, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Timestamp', 'Event', 'Message Code'])
        writer.writerows(events)


def process_log_to_csv(log_file_path):
    # Read the log file
    with open(log_file_path, 'r', encoding='utf-8') as file:
        log_content = file.read()

    # Parse the log
    jobs, reports, events = parse_sap_log(log_content)

    # Save jobs to CSV
    job_headers = ['id', 'name', 'scheduled_time', 'start_time', 'end_time', 'return_code',
                   'scheduled_message_code', 'start_message_code', 'end_message_code', 'remove_message_code']
    save_to_csv(jobs, '../jobs.csv', job_headers)

    # Save reports to CSV
    report_headers = ['id', 'file_name', 'start_time', 'end_time', 'start_message_code', 'end_message_code']
    save_to_csv(reports, '../reports.csv', report_headers)

    # Save events to CSV
    save_events_to_csv(events, '../events.csv')

    print("Data has been saved to jobs.csv, reports.csv, and events.csv")


if __name__ == "__main__":
    log_file_path = '../logs/2024-10-05 09:31:48;2024-10-05 20:18:04.txt'
    process_log_to_csv(log_file_path)