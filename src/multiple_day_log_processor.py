import os
import time
from src.utils import (
    PROJECT_ROOT, extract_time_range, parse_sap_log, save_to_csv,
    save_events_to_csv, monitor_resources, save_benchmarks, read_log_file
)

def process_log_file(log_file_path, filename):
    file_start_time = time.time()

    log_content = read_log_file(log_file_path)
    if not log_content:
        return 0, 0, 0

    start_time, end_time = extract_time_range(log_content)
    if start_time and end_time:
        print(f"Log period: {start_time} to {end_time}")
    else:
        print("Unable to extract time range from the log file.")
        print(f"File size: {os.path.getsize(log_file_path)} bytes")
        print(f"First 100 characters: {log_content[:100]}")

    jobs, reports, events = parse_sap_log(log_content)

    # Append results to CSV files
    job_headers = ['id', 'name', 'scheduled_time', 'start_time', 'end_time', 'return_code',
                   'scheduled_message_code', 'start_message_code', 'end_message_code', 'remove_message_code']
    save_to_csv(jobs, 'combined_jobs.csv', job_headers, mode='a')

    report_headers = ['id', 'file_name', 'start_time', 'end_time', 'start_message_code', 'end_message_code']
    save_to_csv(reports, 'combined_reports.csv', report_headers, mode='a')

    save_events_to_csv(events, 'combined_events.csv', mode='a')

    # Calculate processing time and monitor resource usage
    file_end_time = time.time()
    file_processing_time = file_end_time - file_start_time
    cpu_usage, ram_usage = monitor_resources()

    print(f"Processed {filename} in {file_processing_time:.2f} seconds")
    print(f"CPU usage: {cpu_usage:.2f}%, RAM usage: {ram_usage:.2f} MB")

    return file_processing_time, cpu_usage, ram_usage

def process_logs_to_csv(logs_folder):
    processing_times = []
    resource_usage = []
    peak_cpu = 0
    peak_ram = 0

    total_start_time = time.time()

    logs_path = os.path.join(PROJECT_ROOT, logs_folder)

    # Clear existing CSV files
    for csv_file in ['combined_jobs.csv', 'combined_reports.csv', 'combined_events.csv']:
        csv_path = os.path.join(PROJECT_ROOT, 'csv', csv_file)
        if os.path.exists(csv_path):
            os.remove(csv_path)

    for filename in os.listdir(logs_path):
        if filename.endswith('.LOG.txt'):
            log_file_path = os.path.join(logs_path, filename)
            print(f"Processing file: {filename}")

            file_processing_time, cpu_usage, ram_usage = process_log_file(log_file_path, filename)

            processing_times.append((filename, file_processing_time))
            resource_usage.append((filename, cpu_usage, ram_usage))
            peak_cpu = max(peak_cpu, cpu_usage)
            peak_ram = max(peak_ram, ram_usage)

    # Calculate and print total processing time
    total_end_time = time.time()
    total_processing_time = total_end_time - total_start_time

    # Calculate average CPU and RAM usage
    avg_cpu = sum(usage[1] for usage in resource_usage) / len(resource_usage) if resource_usage else 0
    avg_ram = sum(usage[2] for usage in resource_usage) / len(resource_usage) if resource_usage else 0

    print("\nCombined data has been saved to csv/combined_jobs.csv, csv/combined_reports.csv, and csv/combined_events.csv")

    # Save benchmarks
    benchmarks = [
        (filename, process_time, cpu_usage, ram_usage)
        for (filename, process_time), (_, cpu_usage, ram_usage) in zip(processing_times, resource_usage)
    ]
    benchmarks.append(('Total', total_processing_time, '', ''))
    benchmarks.append(('Average', total_processing_time / len(processing_times), avg_cpu, avg_ram))
    benchmarks.append(('Peak', '', peak_cpu, peak_ram))

    save_benchmarks(benchmarks, 'multiple_benchmarks.csv')
    print("Benchmarks have been saved to benchmarks/multiple_benchmarks.csv")

if __name__ == "__main__":
    logs_folder = 'logs'
    process_logs_to_csv(logs_folder)