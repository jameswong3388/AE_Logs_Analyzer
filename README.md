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
│   ├── jobs_analyzer.py
│   ├── multiple_day_log_processor.py
│   └── single_day_log_processcor.py
└── .gitignore
```

## Key Components

1. **jobs_analyzer.py**: This script analyzes the processed job data, generating statistics and visualizations about job performance, duration, and concurrency.

2. **multiple_day_log_processor.py**: Processes multiple log files, typically spanning several days, and combines the data into a single set of output files.

3. **single_day_log_processcor.py**: Processes a single day's log file, extracting job and report information.

## Features

- Parse SAP log files and extract job and report information
- Process single-day or multiple-day log files
- Generate CSV files with parsed data:
  - Jobs data
  - Reports data
  - Event logs
- Analyze job performance:
  - Determine average and maximum job durations
  - Identify most common jobs
- Visualize data:
  - Plot concurrent jobs over time
  - Create histograms of job durations

## How to Use

1. Place your SAP log files in the `src/logs` directory.

2. To process a single day's log:
   ```
   python src/single_day_log_processcor.py
   ```

3. To process multiple days' logs:
   ```
   python src/multiple_day_log_processor.py
   ```

4. To analyze the processed data:
   ```
   python src/jobs_analyzer.py
   ```

5. Check the `src/csv` directory for the output CSV files and the `src/graphs` directory for generated visualizations.

## Requirements

- Python 3.x
- pandas
- matplotlib

## Setup

1. Clone the repository
2. Create and activate a virtual environment (Optional):
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```
3. Install the required packages:
   ```
   pip install pandas matplotlib
   ```

## Notes

- Ensure that your log files are in the correct format expected by the parsers.
- The project uses a virtual environment (`.venv`) to manage dependencies.
- Output files are saved in the `src/csv` and `src/graphs` directories.

## Contributing

Feel free to fork this project and submit pull requests with any enhancements or bug fixes. Please ensure that your code adheres to the existing style and includes appropriate tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.