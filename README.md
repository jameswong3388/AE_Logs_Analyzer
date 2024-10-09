# AE Log Analysis

## Project Overview

The AE Log Analysis project is a Python-based tool designed to process and analyze log files from an SAP system. It provides functionality to parse log files, extract relevant information about jobs and reports, and generate insightful analytics.

## Project Structure

```
root
├── src
│   ├── csv
│   ├── graphs
│   ├── logs
│   ├── benchmarks
│   ├── results
│   ├── advance_analyzer.py
│   ├── jobs_analyzer.py
│   ├── multiple_day_log_processor.py
│   └── single_day_log_processor.py
└── .gitignore
```

## Key Components

1. **advance_analyzer.py**: This script performs advanced analysis on the processed data, including job patterns, error patterns, and system load over time.

2. **jobs_analyzer.py**: Analyzes the processed job data, generating statistics and visualizations about job performance, duration, and concurrency.

3. **multiple_day_log_processor.py**: Processes multiple log files, typically spanning several days, and combines the data into a single set of output files.

4. **single_day_log_processor.py**: Processes a single day's log file, extracting job and report information.

## Features

- Parse SAP log files and extract job, report, and event information
- Process single-day or multiple-day log files
- Generate CSV files with parsed data:
  - Jobs data
  - Reports data
  - Event logs
- Analyze job performance:
  - Determine average and maximum job durations
  - Identify most common jobs
  - Analyze job patterns over time
- Analyze error patterns
- Analyze system load over time
- Visualize data:
  - Plot concurrent jobs over time
  - Create histograms of job durations
  - Graph job distribution by hour of day
  - Graph error message code distribution
  - Graph system load over time

## How to Use

1. Place your SAP log files in the `src/logs` directory.

2. To process a single day's log:
   ```
   python src/single_day_log_processor.py
   ```

3. To process multiple days' logs:
   ```
   python src/multiple_day_log_processor.py
   ```

4. To perform basic analysis on the processed data:
   ```
   python src/jobs_analyzer.py
   ```

5. To perform advanced analysis on the processed data:
   ```
   python src/advance_analyzer.py
   ```

6. Check the following directories for output:
   - `src/csv`: Output CSV files
   - `src/graphs`: Generated visualizations
   - `src/results`: Additional analysis results
   - `src/benchmarks`: Processing time information

## Requirements

- Python 3.x
- pandas
- matplotlib
- seaborn

## Setup

1. Clone the repository
2. Create and activate a virtual environment (Optional):
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```
3. Install the required packages:
   ```
   pip install pandas matplotlib seaborn
   ```

## Notes

- Ensure that your log files are in the correct format expected by the parsers.
- The project uses a virtual environment (`.venv`) to manage dependencies.
- The scripts attempt to decode log files using multiple encodings (utf-8, iso-8859-1, windows-1252, ascii) to handle potential encoding issues.
- Processing times for log files are recorded and saved for performance analysis.

## Contributing

Feel free to fork this project and submit pull requests with any enhancements or bug fixes. Please ensure that your code adheres to the existing style and includes appropriate tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.