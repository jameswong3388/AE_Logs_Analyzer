import os
import pandas as pd
import matplotlib.pyplot as plt

# Define the project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def load_jobs_data(file_path):
    df = pd.read_csv(file_path)

    # Convert time columns to datetime
    time_columns = ['scheduled_time', 'start_time', 'end_time']
    for col in time_columns:
        df[col] = pd.to_datetime(df[col], format='mixed', errors='coerce')

    return df

def get_concurrent_jobs(df):
    events = []
    for _, row in df.iterrows():
        if pd.notnull(row['start_time']):
            events.append((row['start_time'], 1))  # Job start
        if pd.notnull(row['end_time']):
            events.append((row['end_time'], -1))  # Job end

    events.sort(key=lambda x: x[0])

    concurrent_jobs = []
    current_count = 0
    for time, change in events:
        current_count += change
        current_count = max(0, current_count)
        concurrent_jobs.append((time, current_count))

    return pd.DataFrame(concurrent_jobs, columns=['timestamp', 'concurrent_jobs'])

def analyze_jobs(df):
    total_jobs = len(df)
    completed_jobs = df['end_time'].notna().sum()
    success_rate = (df['return_code'] == '0').mean() * 100 if 'return_code' in df.columns else None

    df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60  # Duration in minutes
    avg_duration = df['duration'].mean()
    max_duration = df['duration'].max()

    print(f"Total Jobs: {total_jobs}")
    print(f"Completed Jobs: {completed_jobs}")
    if success_rate is not None:
        print(f"Success Rate: {success_rate:.2f}%")
    print(f"Average Job Duration: {avg_duration:.2f} minutes")
    print(f"Maximum Job Duration: {max_duration:.2f} minutes")

    # Most common job names
    print("\nTop 5 Most Common Jobs:")
    top_jobs = df['name'].value_counts().head()
    print(top_jobs)

    # Top 5 longest-running jobs
    longest_jobs = df.nlargest(10, 'duration')
    print("\nTop 5 Longest-Running Jobs:")
    for _, job in longest_jobs.iterrows():
        print(f"Job Name: {job['name']}")
        print(f"  RunID: {job['id']}")
        print(f"  Duration: {job['duration']:.2f} minutes")
        print(f"  Start Time: {job['start_time']}")
        print(f"  End Time: {job['end_time']}")
        print(f"  Return Code: {job['return_code']}")
        print()

    # Save analysis results to CSV files
    summary_data = {
        'Metric': ['Total Jobs', 'Completed Jobs', 'Success Rate', 'Average Job Duration', 'Maximum Job Duration'],
        'Value': [total_jobs, completed_jobs, success_rate, avg_duration, max_duration]
    }
    pd.DataFrame(summary_data).to_csv(os.path.join(PROJECT_ROOT, 'results', 'job_summary.csv'), index=False)

    top_jobs.to_csv(os.path.join(PROJECT_ROOT, 'results', 'top_common_jobs.csv'))

    longest_jobs[['name', 'id', 'duration', 'start_time', 'end_time', 'return_code']].to_csv(
        os.path.join(PROJECT_ROOT, 'results', 'longest_running_jobs.csv'), index=False)

    return df

def plot_concurrent_jobs(concurrent_jobs):
    plt.figure(figsize=(12, 6))
    plt.plot(concurrent_jobs['timestamp'], concurrent_jobs['concurrent_jobs'])
    plt.title('Number of Concurrent Jobs Over Time')
    plt.xlabel('Time')
    plt.ylabel('Number of Concurrent Jobs')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(PROJECT_ROOT, 'graphs', 'concurrent_jobs.png'))
    plt.close()

    # Save concurrent jobs data to CSV
    concurrent_jobs.to_csv(os.path.join(PROJECT_ROOT, 'results', 'concurrent_jobs.csv'), index=False)

def plot_job_duration_histogram(df):
    plt.figure(figsize=(10, 6))
    df['duration'].hist(bins=50)
    plt.title('Distribution of Job Durations')
    plt.xlabel('Duration (minutes)')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(PROJECT_ROOT, 'graphs', 'job_duration_histogram.png'))
    plt.close()

    # Save job duration data to CSV
    df[['name', 'id', 'duration']].to_csv(os.path.join(PROJECT_ROOT, 'results', 'job_durations.csv'), index=False)

def main():
    # Load the jobs data
    df = load_jobs_data(os.path.join(PROJECT_ROOT, 'csv', 'combined_jobs.csv'))

    # Analyze jobs
    df = analyze_jobs(df)

    # Get concurrent jobs data
    concurrent_jobs = get_concurrent_jobs(df)

    # Plot concurrent jobs
    plot_concurrent_jobs(concurrent_jobs)

    # Plot job duration histogram
    plot_job_duration_histogram(df)

    print("\nAnalysis complete. Graphs have been saved in the 'graphs' directory and CSV files in the 'csv' directory.")

if __name__ == "__main__":
    main()