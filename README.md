# AE Log Analysis

## Project Overview

The AE Log Analysis project is a Python-based tool suite designed to process and analyze SAP system log files. It provides comprehensive functionality for parsing log files, extracting job and report information, and generating detailed analytics in both batch and real-time modes.

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
│   ├── jobs_analyzer.py
│   ├── live_log_processor.py
│   ├── multiple_day_log_processor.py
│   └── single_day_log_processor.py
└── README.md
```

## Key Components

### 1. Jobs Analyzer (`jobs_analyzer.py`)
- **Enhanced Job Analysis**:
  - Top 20 longest-running jobs identification
  - Detailed job duration analysis
  - Wait time analysis (scheduled vs. actual start time)
  - Success/failure rate tracking
  - Comprehensive job status reporting
  - Concurrent job analysis
  - Resource utilization tracking
  
- **Visualization Features**:
  - Job distribution by hour
  - Duration distribution histograms
  - System load trends
  - Concurrent jobs visualization with heatmap
  - Error distribution analysis

- **Output Formats**:
  - Detailed CSV reports
  - Formatted console output
  - Visual graphs and charts

### 2. Live Log Processor (`live_log_processor.py`)
- Real-time log file monitoring
- Automatic processing of new logs
- Resource usage tracking
- Performance benchmarking
- Thread-safe processing
- File lock management
- Duplicate processing prevention

### 3. Multiple Day Log Processor (`multiple_day_log_processor.py`)
- Batch processing capabilities
- Aggregate statistics
- Combined data output
- Resource monitoring
- Performance benchmarking

### 4. Single Day Log Processor (`single_day_log_processor.py`)
- Individual log file processing
- Detailed event tracking
- Resource monitoring
- Performance metrics

### 5. Utilities (`utils.py`)
- Enhanced log parsing
- Multiple encoding support
- CSV operations
- Resource monitoring
- Time range extraction
- Benchmark tracking

## Features

### Data Processing
- **Log Parsing**:
  - Multiple encoding support (utf-8, iso-8859-1, windows-1252, ascii)
  - Robust error handling
  - Automatic header detection
  - Thread-safe operations

- **Job Analysis**:
  - Duration calculation and validation
  - Wait time analysis
  - Status tracking
  - Return code analysis
  - Concurrent job monitoring

- **Performance Tracking**:
  - CPU usage monitoring
  - RAM utilization
  - Processing time benchmarks
  - Resource peaks tracking

### Analysis Capabilities
- **Job Metrics**:
  - Top 20 longest-running jobs
  - Success/failure rates
  - Average and maximum durations
  - Wait time analysis
  - Concurrent job patterns
  - Job frequency analysis

- **System Analysis**:
  - Resource utilization
  - Performance benchmarking
  - Error pattern identification
  - Load distribution analysis

### Visualization
- **Distribution Analysis**:
  - Hourly job distribution
  - Duration patterns
  - Concurrent job trends
  - Error frequency visualization

- **System Monitoring**:
  - Resource usage graphs
  - Load pattern visualization
  - Performance trend analysis

## Usage Instructions

### 1. Real-time Processing
```bash
python src/live_log_processor.py
```
- Monitor `src/live_logs` directory for new files
- Real-time processing and analysis
- Automatic benchmark generation

### 2. Batch Processing
Single log file:
```bash
python src/single_day_log_processor.py
```

Multiple log files:
```bash
python src/multiple_day_log_processor.py
```

### 3. Analysis
```bash
python src/jobs_analyzer.py
```

### Output Locations
- Processed data: `src/csv/`
- Analysis results: `src/results/`
- Visualizations: `src/graphs/`
- Performance metrics: `src/benchmarks/`

## Requirements

### Python Dependencies
```
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
watchdog>=2.1.0
psutil>=5.8.0
```

### Installation
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Best Practices

### 1. Data Management
- Regular archiving of processed logs
- Periodic cleanup of temporary files
- Monitoring of disk space usage

### 2. Performance Optimization
- Process large batches during off-peak hours
- Monitor resource utilization
- Regular benchmark review
- Clean up old results periodically

### 3. Analysis Workflow
- Review job summary reports regularly
- Monitor error patterns
- Track system load trends
- Analyze concurrent job patterns

## Contributing
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit pull request with documentation

### Code Standards
- PEP 8 compliance
- Comprehensive error handling
- Clear documentation
- Test coverage
- Type hints (where applicable)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.