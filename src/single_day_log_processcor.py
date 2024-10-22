import os
import time

from src.utils import (
    PROJECT_ROOT, parse_sap_log, save_to_csv, save_events_to_csv,
    monitor_resources, save_benchmarks, read_log_file
)


def process_log_to_csv(log_file_path):
    start_time = time.time()
    resource_usage = []
    peak_cpu = peak_ram = 0

    log_content = read_log_file(log_file_path)
    if not log_content:
        return

    jobs, reports, events = parse_sap_log(log_content)

    cpu_usage, ram_usage = monitor_resources()
    peak_cpu = max(peak_cpu, cpu_usage)
    peak_ram = max(peak_ram, ram_usage)
    resource_usage.append((cpu_usage, ram_usage))

    job_headers = ['id', 'name', 'scheduled_time', 'start_time', 'end_time', 'return_code',
                   'scheduled_message_code', 'start_message_code', 'end_message_code', 'remove_message_code']
    save_to_csv(jobs, 'jobs.csv', job_headers)

    report_headers = ['id', 'file_name', 'start_time', 'end_time', 'start_message_code', 'end_message_code']
    save_to_csv(reports, 'reports.csv', report_headers)

    save_events_to_csv(events, 'events.csv')

    processing_time = time.time() - start_time
    avg_cpu = sum(usage[0] for usage in resource_usage) / len(resource_usage)
    avg_ram = sum(usage[1] for usage in resource_usage) / len(resource_usage)

    print(f"Data has been saved to csv/jobs.csv, csv/reports.csv, and csv/events.csv")
    print(f"Processing time: {processing_time:.2f} seconds")
    print(f"Peak CPU usage: {peak_cpu:.2f}%")
    print(f"Peak RAM usage: {peak_ram:.2f} MB")
    print(f"Average CPU usage: {avg_cpu:.2f}%")
    print(f"Average RAM usage: {avg_ram:.2f} MB")

    benchmarks = [
        (os.path.basename(log_file_path), processing_time, peak_cpu, peak_ram, avg_cpu, avg_ram)
    ]

    save_benchmarks(benchmarks, 'single_benchmarks.csv')
    print("Benchmarks have been saved to benchmarks/single_benchmarks.csv")

if __name__ == "__main__":
    log_file_path = os.path.join(PROJECT_ROOT, 'logs', '189229440.LOG.txt')
    process_log_to_csv(log_file_path)