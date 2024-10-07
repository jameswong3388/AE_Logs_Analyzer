import csv
import os
import re
import time
from collections import defaultdict
from datetime import datetime, timedelta


def extract_time_range(log_content):
    lines = log_content.split('\n')
    first_line = next((line for line in lines if line.strip()), "")
    last_line = next((line for line in reversed(lines) if line.strip()), "")

    start_time_match = re.search(r'(\d{8}/\d{6}\.\d{3})', first_line)
    end_time_match = re.search(r'(\d{8}/\d{6}\.\d{3})', last_line)

    if start_time_match and end_time_match:
        start_time = datetime.strptime(start_time_match.group(1), '%Y%m%d/%H%M%S.%f')
        end_time = datetime.strptime(end_time_match.group(1), '%Y%m%d/%H%M%S.%f')
        return start_time, end_time
    else:
        print("Debug: First line:", first_line)
        print("Debug: Last line:", last_line)
        return None, None

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


def process_logs_to_csv(logs_folder):
    all_jobs = defaultdict(lambda: defaultdict(str))
    all_reports = defaultdict(dict)
    all_events = []
    processing_times = []

    # List of encodings to try
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252', 'ascii']

    total_start_time = time.time()

    # Process each log file in the folder
    for filename in os.listdir(logs_folder):
        if filename.endswith('.LOG.txt'):
            log_file_path = os.path.join(logs_folder, filename)
            print(f"Processing file: {filename}")

            file_start_time = time.time()

            for encoding in encodings:
                try:
                    with open(log_file_path, 'r', encoding=encoding) as file:
                        log_content = file.read()

                    start_time, end_time = extract_time_range(log_content)
                    if start_time and end_time:
                        print(f"Log period: {start_time} to {end_time}")
                    else:
                        print("Unable to extract time range from the log file.")
                        print(f"File size: {os.path.getsize(log_file_path)} bytes")
                        print(f"First 100 characters: {log_content[:100]}")

                    jobs, reports, events = parse_sap_log(log_content)

                    # Merge the results
                    all_jobs.update(jobs)
                    all_reports.update(reports)
                    all_events.extend(events)

                    # Calculate and record processing time for this file
                    file_end_time = time.time()
                    file_processing_time = file_end_time - file_start_time
                    processing_times.append((filename, file_processing_time))

                    print(f"Processed {filename} in {file_processing_time:.2f} seconds")

                    # If we've successfully read and processed the file, break out of the encoding loop
                    break
                except UnicodeDecodeError:
                    # If this encoding didn't work, try the next one
                    if encoding == encodings[-1]:
                        print(f"Error: Unable to decode file {filename} with any of the attempted encodings.")
                        processing_times.append((filename, 0))  # Record 0 time for failed processing
                except Exception as e:
                    print(f"Error processing file {filename}: {str(e)}")
                    processing_times.append((filename, 0))  # Record 0 time for failed processing
                    break  # Break the encoding loop if there's a non-encoding related error

    # Sort events by timestamp
    all_events.sort(key=lambda x: x[0])

    # Save combined results to CSV
    job_headers = ['id', 'name', 'scheduled_time', 'start_time', 'end_time', 'return_code',
                   'scheduled_message_code', 'start_message_code', 'end_message_code', 'remove_message_code']
    save_to_csv(all_jobs, 'combined_jobs.csv', job_headers)

    report_headers = ['id', 'file_name', 'start_time', 'end_time', 'start_message_code', 'end_message_code']
    save_to_csv(all_reports, 'combined_reports.csv', report_headers)

    save_events_to_csv(all_events, 'combined_events.csv')

    # Calculate and print total processing time
    total_end_time = time.time()
    total_processing_time = total_end_time - total_start_time

    print("\nProcessing Time Summary:")
    for filename, process_time in processing_times:
        print(f"{filename}: {process_time:.2f} seconds")

    print(f"\nTotal processing time: {total_processing_time:.2f} seconds")
    print(f"Average processing time per file: {total_processing_time / len(processing_times):.2f} seconds")

    print("\nCombined data has been saved to combined_jobs.csv, combined_reports.csv, and combined_events.csv")

    # Save processing times to CSV
    with open('processing_times.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Filename', 'Processing Time (seconds)'])
        writer.writerows(processing_times)
        writer.writerow(['Total', total_processing_time])
        writer.writerow(['Average', total_processing_time / len(processing_times)])

    print("Processing times have been saved to processing_times.csv")

if __name__ == "__main__":
    logs_folder = 'logs'
    process_logs_to_csv(logs_folder)
