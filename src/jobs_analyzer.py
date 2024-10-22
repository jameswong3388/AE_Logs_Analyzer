import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class JobsAnalyzer:
    def __init__(self, project_root=None):
        """Initialize the Ultimate Analyzer with project directory configuration."""
        self.project_root = project_root or os.path.dirname(os.path.abspath(__file__))
        self.jobs_df = None
        self.reports_df = None
        self.events_df = None

    def load_data(self):
        """Load data from CSV files and convert time columns to datetime."""
        print("Loading data files...")

        # Load DataFrames
        self.jobs_df = pd.read_csv(os.path.join(self.project_root, 'csv', 'combined_jobs.csv'))
        self.reports_df = pd.read_csv(os.path.join(self.project_root, 'csv', 'combined_reports.csv'))
        self.events_df = pd.read_csv(os.path.join(self.project_root, 'csv', 'combined_events.csv'))

        # Convert time columns to datetime
        time_columns = ['scheduled_time', 'start_time', 'end_time']
        for col in time_columns:
            if col in self.jobs_df.columns:
                self.jobs_df[col] = pd.to_datetime(self.jobs_df[col], format='%Y-%m-%d %H:%M:%S', errors='coerce')

        for col in ['start_time', 'end_time']:
            if col in self.reports_df.columns:
                self.reports_df[col] = pd.to_datetime(self.reports_df[col], format='%Y-%m-%d %H:%M:%S', errors='coerce')

        if 'Timestamp' in self.events_df.columns:
            self.events_df['Timestamp'] = pd.to_datetime(self.events_df['Timestamp'], format='%Y-%m-%d %H:%M:%S',
                                                         errors='coerce')

        print("Data loading complete.")

    def analyze_jobs(self):
        """Perform comprehensive job analysis."""
        print("\nAnalyzing jobs...")

        # Calculate basic job metrics
        total_jobs = len(self.jobs_df)
        completed_jobs = self.jobs_df['end_time'].notna().sum()
        success_rate = (self.jobs_df[
                            'return_code'] == '0').mean() * 100 if 'return_code' in self.jobs_df.columns else None

        # Calculate job durations
        self.jobs_df['duration'] = (self.jobs_df['end_time'] - self.jobs_df['start_time']).dt.total_seconds() / 60
        avg_duration = self.jobs_df['duration'].mean()
        max_duration = self.jobs_df['duration'].max()

        # Get most common jobs
        top_jobs = self.jobs_df['name'].value_counts().head()

        # Get longest running jobs
        longest_jobs = self.jobs_df.nlargest(5, 'duration')[
            ['name', 'id', 'duration', 'start_time', 'end_time', 'return_code']]

        # Save results
        results = {
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'success_rate': success_rate,
            'avg_duration': avg_duration,
            'max_duration': max_duration,
            'top_jobs': top_jobs,
            'longest_jobs': longest_jobs
        }

        self._save_job_analysis(results)
        return results

    def analyze_patterns(self):
        """Analyze various patterns in the data."""
        print("\nAnalyzing patterns...")

        # Analyze hourly patterns
        self.jobs_df['hour'] = self.jobs_df['start_time'].dt.hour
        hourly_patterns = self.jobs_df.groupby('hour').size()

        # Analyze daily patterns
        self.jobs_df['date'] = self.jobs_df['start_time'].dt.date
        daily_patterns = self.jobs_df.groupby('date').size()

        # Analyze error patterns
        error_events = self.events_df[self.events_df['Event'].str.contains('error', case=False, na=False)]
        error_patterns = error_events['Message Code'].value_counts()

        patterns = {
            'hourly': hourly_patterns,
            'daily': daily_patterns,
            'errors': error_patterns
        }

        self._save_pattern_analysis(patterns)
        return patterns

    def analyze_system_load(self):
        """Analyze system load and performance metrics."""
        print("\nAnalyzing system load...")

        # Get concurrent jobs data
        concurrent_df = self.get_concurrent_jobs_data()

        # Calculate system metrics
        system_metrics = {
            'peak_concurrent_jobs': concurrent_df['concurrent_jobs'].max(),
            'avg_concurrent_jobs': concurrent_df['concurrent_jobs'].mean(),
            'total_execution_time': (self.jobs_df['end_time'].max() - self.jobs_df[
                'start_time'].min()).total_seconds() / 3600,
            'jobs_per_hour': len(self.jobs_df) / (
                    (self.jobs_df['end_time'].max() - self.jobs_df['start_time'].min()).total_seconds() / 3600)
        }

        self._save_system_analysis(system_metrics, concurrent_df)
        return system_metrics, concurrent_df

    def get_concurrent_jobs_data(self):
        """Calculate concurrent jobs data with detailed time series."""
        events = []

        # Create events for job starts and ends
        for _, row in self.jobs_df.iterrows():
            if pd.notnull(row['start_time']):
                events.append((row['start_time'], 1, row['name']))
            if pd.notnull(row['end_time']):
                events.append((row['end_time'], -1, row['name']))

        # Sort events by timestamp
        events.sort(key=lambda x: x[0])

        # Calculate concurrent jobs over time
        concurrent_jobs = []
        active_jobs = set()

        for time, change, job_name in events:
            if change == 1:
                active_jobs.add(job_name)
            else:
                active_jobs.discard(job_name)

            concurrent_jobs.append({
                'timestamp': time,
                'concurrent_jobs': len(active_jobs),
                'active_jobs': ', '.join(list(active_jobs)[:3]) + (
                    f' (+{len(active_jobs) - 3} more)' if len(active_jobs) > 3 else '')
            })

        return pd.DataFrame(concurrent_jobs)

    def generate_visualizations(self):
        """Generate comprehensive visualizations."""
        print("\nGenerating visualizations...")

        # Create graphs directory if it doesn't exist
        graphs_dir = os.path.join(self.project_root, 'graphs')
        os.makedirs(graphs_dir, exist_ok=True)

        # 1. Job Distribution by Hour
        plt.figure(figsize=(12, 6))
        self.jobs_df['hour'].value_counts().sort_index().plot(kind='bar')
        plt.title('Job Distribution by Hour of Day')
        plt.xlabel('Hour')
        plt.ylabel('Number of Jobs')
        plt.tight_layout()
        plt.savefig(os.path.join(graphs_dir, 'job_distribution_by_hour.png'))
        plt.close()

        # 2. Job Duration Distribution
        plt.figure(figsize=(12, 6))
        sns.histplot(data=self.jobs_df, x='duration', bins=50)
        plt.title('Distribution of Job Durations')
        plt.xlabel('Duration (minutes)')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(os.path.join(graphs_dir, 'job_duration_distribution.png'))
        plt.close()

        # 3. System Load Over Time
        plt.figure(figsize=(12, 6))
        self.jobs_df.groupby('date').size().plot()
        plt.title('System Load Over Time')
        plt.xlabel('Date')
        plt.ylabel('Number of Jobs')
        plt.tight_layout()
        plt.savefig(os.path.join(graphs_dir, 'system_load_over_time.png'))
        plt.close()

        # 4. Error Distribution
        error_events = self.events_df[self.events_df['Event'].str.contains('error', case=False, na=False)]
        plt.figure(figsize=(12, 6))
        error_events['Message Code'].value_counts().head(10).plot(kind='bar')
        plt.title('Top 10 Error Message Codes')
        plt.xlabel('Message Code')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(graphs_dir, 'error_distribution.png'))
        plt.close()

        # 5. Concurrent Jobs Visualization
        concurrent_df = self.get_concurrent_jobs_data()

        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), height_ratios=[2, 1])

        # Plot concurrent jobs over time
        ax1.plot(concurrent_df['timestamp'], concurrent_df['concurrent_jobs'],
                 linewidth=2, color='blue', label='Concurrent Jobs')

        # Add peak markers
        peak_mask = concurrent_df['concurrent_jobs'] == concurrent_df['concurrent_jobs'].max()
        ax1.scatter(concurrent_df[peak_mask]['timestamp'],
                    concurrent_df[peak_mask]['concurrent_jobs'],
                    color='red', s=100, zorder=5, label='Peak Concurrency')

        # Customize the main plot
        ax1.set_title('Concurrent Jobs Over Time', fontsize=14, pad=20)
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Number of Concurrent Jobs')
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.legend()

        # Add daily average line using 'D' frequency
        daily_avg = concurrent_df.set_index('timestamp').resample('D')['concurrent_jobs'].mean()
        ax1.plot(daily_avg.index, daily_avg.values,
                 color='green', linestyle='--', label='Daily Average')

        # Add heatmap showing intensity of job concurrency using 'h' frequency
        daily_hours = concurrent_df.set_index('timestamp').resample('h')['concurrent_jobs'].mean().values
        hours = range(len(daily_hours))
        heatmap = ax2.pcolormesh([hours], [0], [daily_hours], cmap='YlOrRd')
        ax2.set_title('Job Concurrency Heatmap', fontsize=12)
        ax2.set_xlabel('Hours from Start')
        ax2.set_yticks([])

        # Add colorbar
        plt.colorbar(heatmap, ax=ax2, orientation='horizontal', label='Average Concurrent Jobs')

        # Adjust layout and save
        plt.tight_layout()
        plt.savefig(os.path.join(graphs_dir, 'concurrent_jobs_analysis.png'), dpi=300, bbox_inches='tight')
        plt.close()

        print("Visualizations saved in the 'graphs' directory.")

    def _save_job_analysis(self, results):
        """Save job analysis results to CSV."""
        results_dir = os.path.join(self.project_root, 'results')
        os.makedirs(results_dir, exist_ok=True)

        # Save summary metrics
        summary = pd.DataFrame({
            'Metric': ['Total Jobs', 'Completed Jobs', 'Success Rate', 'Average Duration', 'Maximum Duration'],
            'Value': [results['total_jobs'], results['completed_jobs'],
                      f"{results['success_rate']:.2f}%" if results['success_rate'] is not None else 'N/A',
                      f"{results['avg_duration']:.2f} minutes",
                      f"{results['max_duration']:.2f} minutes"]
        })
        summary.to_csv(os.path.join(results_dir, 'job_summary.csv'), index=False)

        # Save top jobs
        results['top_jobs'].to_frame('count').to_csv(os.path.join(results_dir, 'top_jobs.csv'))

        # Save longest jobs
        results['longest_jobs'].to_csv(os.path.join(results_dir, 'longest_jobs.csv'), index=False)

    def _save_pattern_analysis(self, patterns):
        """Save pattern analysis results to CSV."""
        results_dir = os.path.join(self.project_root, 'results')
        os.makedirs(results_dir, exist_ok=True)

        patterns['hourly'].to_frame('count').to_csv(os.path.join(results_dir, 'hourly_patterns.csv'))
        patterns['daily'].to_frame('count').to_csv(os.path.join(results_dir, 'daily_patterns.csv'))
        patterns['errors'].to_frame('count').to_csv(os.path.join(results_dir, 'error_patterns.csv'))

    def _save_system_analysis(self, metrics, concurrent_df):
        """Save system analysis results to CSV."""
        results_dir = os.path.join(self.project_root, 'results')
        os.makedirs(results_dir, exist_ok=True)

        # Save metrics
        pd.DataFrame({
            'Metric': list(metrics.keys()),
            'Value': list(metrics.values())
        }).to_csv(os.path.join(results_dir, 'system_metrics.csv'), index=False)

        # Save concurrent jobs data
        concurrent_df.to_csv(os.path.join(results_dir, 'concurrent_jobs.csv'), index=False)


def main():
    analyzer = JobsAnalyzer()

    try:
        # Load data
        analyzer.load_data()

        # Perform analysis
        job_results = analyzer.analyze_jobs()
        pattern_results = analyzer.analyze_patterns()
        system_results, concurrent_jobs = analyzer.analyze_system_load()

        # Generate visualizations
        analyzer.generate_visualizations()

        print("\nAnalysis complete!")
        print("Results have been saved in the 'results' directory.")
        print("Visualizations have been saved in the 'graphs' directory.")

    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        raise


if __name__ == "__main__":
    main()