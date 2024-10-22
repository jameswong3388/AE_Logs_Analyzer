import time
import sys
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

from src.utils import (
    PROJECT_ROOT, extract_time_range, parse_sap_log, save_to_csv,
    save_events_to_csv, monitor_resources, save_benchmarks, read_log_file
)


class LogFileHandler(FileSystemEventHandler):
    def __init__(self):
        self.processing_times = []
        self.resource_usage = []
        self.peak_cpu = 0
        self.peak_ram = 0

        # Initialize CSV files if they don't exist
        self.initialize_csv_files()

    def initialize_csv_files(self):
        # Define headers
        self.job_headers = ['id', 'name', 'scheduled_time', 'start_time', 'end_time', 'return_code',
                            'scheduled_message_code', 'start_message_code', 'end_message_code', 'remove_message_code']
        self.report_headers = ['id', 'file_name', 'start_time', 'end_time', 'start_message_code', 'end_message_code']

        # Create fresh CSV files if they don't exist
        save_to_csv({}, 'combined_jobs.csv', self.job_headers, mode='w')
        save_to_csv({}, 'combined_reports.csv', self.report_headers, mode='w')
        save_events_to_csv([], 'combined_events.csv', mode='w')

    def process_file(self, file_path):
        filename = os.path.basename(file_path)
        if not filename.endswith('.LOG.txt'):
            return

        print(f"\n[{datetime.now()}] Processing new file: {filename}")

        try:
            file_start_time = time.time()

            # Read and process the log file
            log_content = read_log_file(file_path)
            if not log_content:
                print(f"[{datetime.now()}] Error: Could not read file {filename}")
                return

            # Extract time range
            start_time, end_time = extract_time_range(log_content)
            if start_time and end_time:
                print(f"[{datetime.now()}] Log period: {start_time} to {end_time}")
            else:
                print(f"[{datetime.now()}] Warning: Unable to extract time range from {filename}")

            # Parse log content
            jobs, reports, events = parse_sap_log(log_content)

            # Save to CSV files
            save_to_csv(jobs, 'live_combined_jobs.csv', self.job_headers, mode='a')
            save_to_csv(reports, 'live_combined_reports.csv', self.report_headers, mode='a')
            save_events_to_csv(events, 'live_combined_events.csv', mode='a')

            # Calculate processing metrics
            file_end_time = time.time()
            file_processing_time = file_end_time - file_start_time
            cpu_usage, ram_usage = monitor_resources()

            # Update statistics
            self.processing_times.append((filename, file_processing_time))
            self.resource_usage.append((filename, cpu_usage, ram_usage))
            self.peak_cpu = max(self.peak_cpu, cpu_usage)
            self.peak_ram = max(self.peak_ram, ram_usage)

            # Save updated benchmarks
            self.save_current_benchmarks()

            print(f"[{datetime.now()}] Successfully processed {filename}")
            print(f"Processing time: {file_processing_time:.2f} seconds")
            print(f"CPU usage: {cpu_usage:.2f}%, RAM usage: {ram_usage:.2f} MB")

        except Exception as e:
            print(f"[{datetime.now()}] Error processing {filename}: {str(e)}")

    def save_current_benchmarks(self):
        if not self.processing_times:
            return

        total_time = sum(time for _, time in self.processing_times)
        avg_time = total_time / len(self.processing_times)
        avg_cpu = sum(cpu for _, cpu, _ in self.resource_usage) / len(self.resource_usage)
        avg_ram = sum(ram for _, _, ram in self.resource_usage) / len(self.resource_usage)

        benchmarks = [
            (filename, process_time, cpu_usage, ram_usage)
            for (filename, process_time), (_, cpu_usage, ram_usage)
            in zip(self.processing_times, self.resource_usage)
        ]
        benchmarks.append(('Total', total_time, '', ''))
        benchmarks.append(('Average', avg_time, avg_cpu, avg_ram))
        benchmarks.append(('Peak', '', self.peak_cpu, self.peak_ram))

        save_benchmarks(benchmarks, 'realtime_benchmarks.csv')

    def on_created(self, event):
        if event.is_directory:
            return
        self.process_file(event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            return
        # Wait a short time to ensure file is completely written
        time.sleep(1)
        self.process_file(event.src_path)


def watch_folder(path):
    # Create an observer and handler
    event_handler = LogFileHandler()
    observer = Observer()

    # Schedule the observer
    observer.schedule(event_handler, path, recursive=False)

    # Start the observer
    observer.start()
    print(f"\n[{datetime.now()}] Started watching folder: {path}")
    print("Waiting for new log files...\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] Stopping folder watch...")
        observer.stop()
        observer.join()
        print(f"[{datetime.now()}] Folder watch stopped")


if __name__ == "__main__":
    # Get the logs folder path
    logs_folder = os.path.join(PROJECT_ROOT, 'live_logs')

    # Create the logs folder if it doesn't exist
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
        print(f"Created logs folder at {logs_folder}")

    # Start watching the folder
    watch_folder(logs_folder)