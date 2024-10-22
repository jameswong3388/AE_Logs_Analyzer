# AE Log Analysis

## Project Overview

The AE Log Analysis project is a Python-based tool designed to process and analyze log files from an SAP system. It provides functionality to parse log files, extract relevant information about jobs and reports, and generate insightful analytics in both batch and real-time modes.

## Project Structure

```
root
├── src
│   ├── csv            # Output CSV files for parsed data
│   ├── graphs         # Generated visualizations
│   ├── logs           # Input directory for batch processing
│   ├── live_logs      # Input directory for real-time processing
│   ├── benchmarks     # Performance metrics
│   ├── results        # Analysis results
│   ├── utils.py       # Common utilities and helper functions
│   ├── advance_analyzer.py
│   ├── jobs_analyzer.py
│   ├── live_log_processor.py
│   ├── multiple_day_log_processor.py
│   └── single_day_log_processor.py
└── .gitignore
```

## Key Components

1. **live_log_processor.py**: Real-time log file monitoring and processing system that watches a directory for new log files and processes them automatically.

2. **advance_analyzer.py**: Performs advanced analysis on processed data, including:
   - Job patterns over time
   - Error patterns and frequency
   - System load analysis
   - Trend visualization

3. **jobs_analyzer.py**: Analyzes job data with features for:
   - Concurrent job analysis
   - Job duration statistics
   - Success rate calculation
   - Performance visualization
   - Top job identification

4. **multiple_day_log_processor.py**: Batch processes multiple log files with:
   - Combined data output
   - Resource usage monitoring
   - Performance benchmarking
   - Aggregate statistics

5. **single_day_log_processor.py**: Processes individual log files with:
   - Detailed job tracking
   - Report extraction
   - Event logging
   - Resource monitoring

6. **utils.py**: Core utilities providing:
   - Log parsing functions
   - CSV handling
   - Resource monitoring
   - Time range extraction
   - File operations

## Features

### Data Processing
- Parse SAP log files for jobs, reports, and events
- Support for both batch and real-time processing
- Multiple encoding support (utf-8, iso-8859-1, windows-1252, ascii)
- Automatic header detection and removal

### Analysis Capabilities
- Job Performance Metrics:
  - Total job count and completion rates
  - Average and maximum job durations
  - Success rate analysis
  - Concurrent job tracking
  - Job pattern identification

- System Analysis:
  - Resource usage monitoring (CPU, RAM)
  - Performance benchmarking
  - Error pattern analysis
  - System load tracking

### Visualization
- Job distribution by hour
- Concurrent jobs over time
- Job duration histograms
- Error message distribution
- System load trends

### Output Formats
- Structured CSV files for:
  - Job data
  - Report information
  - Event logs
  - Performance benchmarks
- Visual graphs and charts
- Real-time processing statistics

## Usage Instructions

### Real-time Processing
1. Start the live log processor:
   ```bash
   python src/live_log_processor.py
   ```
2. Place new log files in the `src/live_logs` directory
3. Monitor real-time processing in the console output

### Batch Processing
1. For single log file:
   ```bash
   python src/single_day_log_processor.py
   ```

2. For multiple log files:
   ```bash
   python src/multiple_day_log_processor.py
   ```

3. Run analysis:
   ```bash
   python src/jobs_analyzer.py
   python src/advance_analyzer.py
   ```

### Output Locations
- CSV data: `src/csv/`
- Visualizations: `src/graphs/`
- Analysis results: `src/results/`
- Performance metrics: `src/benchmarks/`

## Requirements

### Python Dependencies
- pandas: Data processing and analysis
- matplotlib: Data visualization
- watchdog: Real-time file monitoring
- psutil: System resource monitoring

### Installation
1. Create and activate virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install pandas matplotlib psutil watchdog
   ```

## Log File Requirements

The system expects log files with the following characteristics:
- Extension: `.LOG.txt`
- Time format: `YYYYMMDD/HHMMSS.mmm`
- Message format: Contains message codes (e.g., 'U########')
- Job entries: Contains job start, end, and status information
- Report entries: Contains report execution details

## Resource Monitoring

The system tracks and reports:
- Processing time per file
- CPU usage percentage
- RAM usage in MB
- Peak resource utilization
- Average resource consumption

## Best Practices

1. Regular Monitoring:
   - Check the benchmarks directory for performance metrics
   - Monitor system resource usage during processing
   - Review error patterns periodically

2. File Management:
   - Maintain organized log directories
   - Archive processed files regularly
   - Monitor disk space usage

3. Performance Optimization:
   - Process large batches during off-peak hours
   - Monitor concurrent job limits
   - Regular cleanup of temporary files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

Please ensure your code:
- Follows existing code style
- Includes appropriate error handling
- Contains necessary documentation
- Includes relevant tests

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.