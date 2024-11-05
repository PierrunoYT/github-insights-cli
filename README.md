# GitHub Insights CLI

A powerful command-line tool for analyzing GitHub repositories and generating comprehensive insights about your project's development metrics.

## Repository

Find the project on GitHub: [https://github.com/PierrunoYT/github-insights-cli](https://github.com/PierrunoYT/github-insights-cli)

## Features

- **Repository Analysis**
  - Commit history analysis
  - Branch statistics
  - Code contribution tracking
  - Development patterns

- **Code Metrics**
  - Language distribution
  - Code complexity analysis
  - Performance metrics
  - Project structure insights

- **Data Visualization**
  - Generate visual reports
  - Multiple export formats
  - Comprehensive statistics
  - Trend analysis

- **CLI Interface**
  - Intuitive command structure
  - Progress indicators
  - Configurable output formats
  - Easy-to-use commands

## Requirements

- Python 3.8+
- Git

## Installation

```bash
# Clone the repository
git clone https://github.com/PierrunoYT/github-insights-cli.git
cd github-insights-cli

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Repository Analysis

```bash
# Analyze the current repository
python main.py analyze .

# Analyze a specific repository
python main.py analyze /path/to/repo

# Analyze with date range
python main.py analyze . --since 2023-01-01 --until 2023-12-31
```

### Output Formats

```bash
# Generate a text report
python main.py analyze . --output text

# Generate a JSON report
python main.py analyze . --output json

# Generate an HTML report with visualizations
python main.py analyze . --output html
```

## Example Output

### Text Report
```
=== GitHub Repository Insights Report ===

== Summary ==
Total Commits: 1,234
Total Contributors: 12
Active Contributors: 8
Primary Language: Python

== Commit Activity ==
Daily Average: 5.2
Weekly Average: 36.4
Monthly Average: 157.3

== Code Distribution ==
Languages:
- Python: 75%
- Markdown: 15%
- Other: 10%
```

### Visual Reports
The HTML reports include interactive visualizations for:
- Commit activity timeline
- Contributor distribution
- Language usage breakdown
- Code complexity metrics

## Project Structure

```
github-insights-cli/
├── main.py              # Entry point script
├── cli.py              # Command-line interface implementation
├── repo_analyzer.py    # Git repository analysis
├── data_processor.py   # Data processing and metrics
├── visualizer.py       # Data visualization and reporting
├── tests/             # Test suite
│   ├── test_repo_analyzer.py
│   ├── test_data_processor.py
│   └── test_visualizer.py
├── cline_docs/        # Project documentation
└── requirements.txt   # Project dependencies
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest

# Run specific test file
pytest tests/test_repo_analyzer.py

# Run with coverage report
pytest --cov=. tests/
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Planned Features

- Real-time repository monitoring
- Custom metrics support
- CI/CD pipeline integration
- Team collaboration insights
- Advanced visualization options
- Machine learning insights
- Security analysis features
- Impact analysis for changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape this project
- Inspired by various Git analysis tools and metrics frameworks
