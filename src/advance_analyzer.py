import os
import pandas as pd
import matplotlib.pyplot as plt

# Define the project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def load_data():
    jobs_df = pd.read_csv(os.path.join(PROJECT_ROOT, 'csv', 'combined_jobs.csv'))
    reports_df = pd.read_csv(os.path.join(PROJECT_ROOT, 'csv', 'combined_reports.csv'))
    events_df = pd.read_csv(os.path.join(PROJECT_ROOT, 'csv', 'combined_events.csv'))

    # Convert time columns to datetime
    time_columns = ['scheduled_time', 'start_time', 'end_time']
    for col in time_columns:
        jobs_df[col] = pd.to_datetime(jobs_df[col], format='%Y-%m-%d %H:%M:%S', errors='coerce')

    reports_df['start_time'] = pd.to_datetime(reports_df['start_time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    reports_df['end_time'] = pd.to_datetime(reports_df['end_time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    events_df['Timestamp'] = pd.to_datetime(events_df['Timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

    return jobs_df, reports_df, events_df


def analyze_job_patterns(jobs_df):
    # Analyze job patterns over time
    jobs_df['hour'] = jobs_df['start_time'].dt.hour
    hourly_job_counts = jobs_df.groupby('hour').size()

    plt.figure(figsize=(12, 6))
    hourly_job_counts.plot(kind='bar')
    plt.title('Job Distribution by Hour of Day')
    plt.xlabel('Hour')
    plt.ylabel('Number of Jobs')
    plt.savefig(os.path.join(PROJECT_ROOT, 'graphs', 'job_distribution_by_hour.png'))
    plt.close()

def analyze_error_patterns(events_df):
    # Analyze error patterns
    error_events = events_df[events_df['Event'].str.contains('error', case=False)]
    error_counts = error_events['Message Code'].value_counts()

    plt.figure(figsize=(12, 6))
    error_counts.plot(kind='bar')
    plt.title('Most Common Error Message Codes')
    plt.xlabel('Message Code')
    plt.ylabel('Count')
    plt.savefig(os.path.join(PROJECT_ROOT, 'graphs', 'error_message_code_distribution.png'))
    plt.close()


def analyze_system_load(jobs_df):
    # Analyze system load over time
    jobs_df['date'] = jobs_df['start_time'].dt.date
    daily_job_counts = jobs_df.groupby('date').size()

    plt.figure(figsize=(12, 6))
    daily_job_counts.plot()
    plt.title('System Load (Number of Jobs) Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Jobs')
    plt.savefig(os.path.join(PROJECT_ROOT, 'graphs', 'system_load_over_time.png'))
    plt.close()

def main():
    jobs_df, reports_df, events_df = load_data()

    analyze_job_patterns(jobs_df)
    analyze_error_patterns(events_df)
    analyze_system_load(jobs_df)

    print("Advanced analysis complete. Results have been saved in the 'graphs' and 'results' directories.")


if __name__ == "__main__":
    main()