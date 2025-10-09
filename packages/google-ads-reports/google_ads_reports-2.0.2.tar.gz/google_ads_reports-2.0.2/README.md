# Google Ads Reports Helper

A Python ETL driver for Google Ads API v21 data extraction and transformation. Simplifies the process of extracting Google Ads data and converting it to database-ready pandas DataFrames with comprehensive optimization features.

[![PyPI version](https://img.shields.io/pypi/v/google-ads-reports)](https://pypi.org/project/google-ads-reports/)
[![Issues](https://img.shields.io/github/issues/machado000/google-ads-reports)](https://github.com/machado000/google-ads-reports/issues)
[![Last Commit](https://img.shields.io/github/last-commit/machado000/google-ads-reports)](https://github.com/machado000/google-ads-reports/commits/main)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/machado000/google-ads-reports/blob/main/LICENSE)

## Features

- **Google Ads API v21**: Latest API version support with full compatibility
- **Pure Python Output**: Returns `list[dict[str, Any]]` - perfect for databases and JSON APIs
- **Serverless Optimized**: No pandas dependency, faster cold starts, lower memory usage
- **Modern Python 3.11+**: Uses latest type hints and language features (supports 3.11-3.13)
- **Flexible Column Naming**: Choose between snake_case or camelCase column conventions  
- **Smart Zero Filtering**: Robust filtering with automatic column detection
- **Custom Reports**: Create custom report configurations with full GAQL support
- **Automatic Retries**: Built-in retry logic for API reliability
- **Comprehensive Error Handling**: Specific exceptions for different failure types
- **Type Safe**: Full type hint support for better IDE experience

## Installation

```bash
pip install google-ads-reports
```

## Quick Start

### 1. Set up credentials

Create a `secrets/google-ads.yaml` file with your Google Ads API credentials:

```yaml
developer_token: "YOUR_DEVELOPER_TOKEN"
client_id: "YOUR_CLIENT_ID"  
client_secret: "YOUR_CLIENT_SECRET"
refresh_token: "YOUR_REFRESH_TOKEN"
```

**References:**
- [Google Ads API Introduction](https://developers.google.com/google-ads/api/docs/get-started/introduction)
- [Developer Token](https://developers.google.com/google-ads/api/docs/get-started/dev-token)
- [Create Credentials](https://developers.google.com/workspace/guides/create-credentials#service-account)

### 2. Basic usage

```python
from datetime import date, timedelta
from google_ads_reports import GAdsReport, GAdsReportModel, load_credentials, get_records_info

# Load credentials
credentials = load_credentials()
client = GAdsReport(credentials)

# Configure report parameters
customer_id = "1234567890"
start_date = date.today() - timedelta(days=7)
end_date = date.today() - timedelta(days=1)

# Extract report data - returns list[dict[str, Any]]
records = client.get_gads_report(
    customer_id=customer_id,
    report_model=GAdsReportModel.keyword_report,
    start_date=start_date,
    end_date=end_date,
    filter_zero_impressions=True,  # Remove rows with zero impressions
    column_naming="snake_case"     # Choose: "snake_case" or "camelCase"
)

# Get dataset information
info = get_records_info(records)
print(f"Shape: {info['shape']}")  # (rows, columns)
print(f"Columns: {info['columns']}")

# Save to CSV or JSON
from google_ads_reports import save_report_to_csv, save_report_to_json
save_report_to_csv(records, "keyword_report.csv")
save_report_to_json(records, "keyword_report.json")
```

### Working with the Data

The library returns `list[dict[str, Any]]` which is perfect for:

```python
# Database insertion
import sqlite3
conn = sqlite3.connect('reports.db')
for record in records:
    # Direct database insertion
    columns = ', '.join(record.keys())
    placeholders = ', '.join(['?' for _ in record])
    values = list(record.values())
    conn.execute(f"INSERT INTO campaigns ({columns}) VALUES ({placeholders})", values)

# JSON APIs
import json
json_data = json.dumps(records)

# Pandas (if needed)
import pandas as pd
df = pd.DataFrame(records)
```

### Column Naming Options

Choose between snake_case (database-friendly) or camelCase (API-consistent):

```python
# Snake case (default) - metrics.impressions → impressions
records_snake = client.get_gads_report(
    customer_id=customer_id,
    report_model=GAdsReportModel.keyword_report,
    start_date=start_date,
    end_date=end_date,
    column_naming="snake_case"  # Default
)

# CamelCase - metrics.impressions → metricsImpressions  
records_camel = client.get_gads_report(
    customer_id=customer_id,
    report_model=GAdsReportModel.keyword_report, 
    start_date=start_date,
    end_date=end_date,
    column_naming="camelCase"
)
```

## Available Report Models

- `GAdsReportModel.adgroup_ad_report` - Ad group ad performance
- `GAdsReportModel.keyword_report` - Keyword performance
- `GAdsReportModel.search_terms_report` - Search terms analysis
- `GAdsReportModel.conversions_report` - Conversion tracking
- `GAdsReportModel.video_report` - Video ad performance
- `GAdsReportModel.assetgroup_report` - Asset group performance

## Custom Reports

Create custom report configurations:

```python
from google_ads_reports import create_custom_report

custom_report = create_custom_report(
    report_name="campaign_performance",
    select=[
        "campaign.name",
        "campaign.status", 
        "segments.date",
        "metrics.impressions",
        "metrics.clicks",
        "metrics.cost_micros"
    ],
    from_table="campaign",
    where="metrics.impressions > 100"
)

records = client.get_gads_report(customer_id, custom_report, start_date, end_date)
```

## Data Processing Features

The package automatically processes data for optimal usability:

### Smart Zero Filtering
Handles multiple zero representations and automatically detects if impression data is available:
```python
records = client.get_gads_report(
    customer_id=customer_id,
    report_model=report_model,
    start_date=start_date,
    end_date=end_date,
    filter_zero_impressions=True  # Removes: 0, "0", 0.0, "0.0", None
)
# Note: Filtering only applied if 'metrics.impressions' column exists in data
```

### Character Encoding Cleanup
- **ASCII Sanitization**: Removes non-ASCII characters for database compatibility  
- **Null Byte Removal**: Strips problematic null bytes (`\x00`)
- **Length Limiting**: Truncates text to 255 characters
- **Whitespace Normalization**: Normalizes whitespace characters

### Flexible Column Naming
Choose your preferred column naming convention:

**Snake Case (Default - Database Friendly):**
- `metrics.impressions` → `impressions`
- `segments.date` → `date`  
- `adGroupCriterion.keyword` → `keyword`

**CamelCase (API Consistent):**
- `metrics.impressions` → `metricsImpressions`
- `segments.date` → `segmentsDate`
- `adGroupCriterion.keyword` → `adGroupCriterionKeyword`

```python
# Choose naming convention
records = client.get_gads_report(
    customer_id=customer_id,
    report_model=report_model,
    start_date=start_date,
    end_date=end_date,
    column_naming="snake_case"  # or "camelCase"
)
```

## Data Output Format

The library returns `list[dict[str, Any]]` which provides maximum flexibility:

```python
# Example output structure
records = [
    {
        "campaign_name": "Summer Campaign",
        "impressions": 1000,
        "clicks": 50,
        "cost": 25.50,
        "date": "2025-10-01"
    },
    {
        "campaign_name": "Winter Campaign", 
        "impressions": 2000,
        "clicks": 100,
        "cost": 45.75,
        "date": "2025-10-01"
    }
]

# Easy conversion to other formats
import pandas as pd
df = pd.DataFrame(records)  # If you need pandas

import json
json_str = json.dumps(records)  # For APIs

# Direct database insertion
for record in records:
    # Insert into database
    pass
```
- `segments.date` → `date`  
- `adGroupCriterion.keyword` → `keyword`

**CamelCase (API Consistent):**
- `metrics.impressions` → `metricsImpressions`
- `segments.date` → `segmentsDate`
- `adGroupCriterion.keyword` → `adGroupCriterionKeyword`

```python
# Choose naming convention
df = client.get_gads_report(
    customer_id=customer_id,
    report_model=report_model,
    start_date=start_date,
    end_date=end_date,
    column_naming="snake_case"  # or "camelCase"
)
```

## Error Handling

The package provides specific exception types for different scenarios:

```python
from google_ads_reports import (
    GAdsReport, 
    AuthenticationError, 
    ValidationError, 
    APIError,
    DataProcessingError,
    ConfigurationError
)

try:
    records = client.get_gads_report(customer_id, report_model, start_date, end_date)
except AuthenticationError:
    # Handle credential issues
    pass
except ValidationError:
    # Handle input validation errors
    pass
except DataProcessingError:
    # Handle data processing errors
    pass
```

## Examples

Check the `examples/` directory for comprehensive usage examples:

- `basic_usage.py` - Simple report extraction
- `multiple_reports.py` - Batch report processing  
- `custom_reports.py` - Custom report creation

## Configuration

### Retry Settings

API calls automatically retry on transient errors with configurable settings:

- **Max attempts**: 3 (default)
- **Base delay**: 1 second
- **Backoff factor**: 2x exponential
- **Max delay**: 30 seconds

### Logging

Configure logging level:

```python
from google_ads_reports import setup_logging
import logging

setup_logging(level=logging.DEBUG)  # Enable debug logging
```

## Requirements

- Python 3.11-3.13
- google-ads >= 24.0.0 (Google Ads API v21 support)
- PyYAML >= 6.0.0
- python-dotenv >= 1.0.0
- tqdm >= 4.65.0

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
- pandas >= 2.0.0
- PyYAML >= 6.0.0
- python-dotenv >= 1.0.0
- tqdm >= 4.65.0

## Development

For development installation:

```bash
git clone https://github.com/machado000/google-ads-reports
cd google-ads-reports
pip install -e ".[dev]"
```

## License

GPL License. See [LICENSE](LICENSE) file for details.

## Support

- [Documentation](https://github.com/machado000/google-ads-reports#readme)
- [Issues](https://github.com/machado000/google-ads-reports/issues)
- [Examples](examples/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
